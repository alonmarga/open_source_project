from airflow.decorators import dag, task
from datetime import datetime, timedelta
import orjson as json
import requests
import pandas as pd
import random
import os
import boto3
from botocore.exceptions import ClientError


from app.db import query_db, batch_insert

default_args = {
    'owner': 'Alon Margalit',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='Create_data',
    default_args=default_args,
    schedule_interval=timedelta(minutes=30),  # Run twice an hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example']
)
def data_fake_dag():
    @task()
    def data_from_mockaroo():
        try:
            response = requests.get(os.environ.get("MOCKAROO_URL"))
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data)  # Convert data to DataFrame for further processing
        except requests.exceptions.RequestException as req_err:
            print(f"data_from_mockaroo Request error: {req_err}")
            return pd.DataFrame()  # Return empty DataFrame on error
        except ValueError as val_err:
            print(f"data_from_mockaroo JSON decoding failed: {val_err}")
            return pd.DataFrame()
        except Exception as e:
            print(f"data_from_mockaroo An unexpected error occurred: {e}")
            return pd.DataFrame()


    @task()
    def get_product_from_db():
        try:
            # Query to get all products with their categories
            query = """
                SELECT i.product_id,
                       c.category_name as category,
                       i.product_name as name,
                       i.brand,
                       i.price::float as price
                FROM dev_items i
                JOIN dev_categories c ON i.category_id = c.category_id
                ORDER BY c.category_name, i.product_name, i.brand;
            """

            # Execute query using query_db function
            products_data = query_db(query)

            transformed_data = {
                "categories": [],
                "products": {}
            }

            for row in products_data:
                category = row['category']

                # Add category to categories list if not exists
                if category not in transformed_data["categories"]:
                    transformed_data["categories"].append(category)
                    transformed_data["products"][category] = []

                # Find existing product or create new one
                product = next(
                    (p for p in transformed_data["products"][category]
                     if p["name"] == row["name"]),
                    None
                )

                if product is None:
                    product = {
                        "name": row["name"],
                        "brands": []
                    }
                    transformed_data["products"][category].append(product)

                # Add brand info
                product["brands"].append({
                    "brand": row["brand"],
                    "price": row["price"]  # Already converted to float in the query
                })

            return transformed_data

        except Exception as e:
            print(f'get_product_file Unexpected error: {e}')
            return {}

    @task(multiple_outputs=True)
    def generate_orders(customers_df, products_data, max_orders=5, max_items=3):
        try:
            orders = []
            for _, customer in customers_df.iterrows():
                customer_id = customer["id"]
                num_orders = random.randint(1, max_orders)
                for _ in range(num_orders):
                    order_date = datetime.now() - timedelta(days=random.randint(0, 30))
                    ship_date = order_date + timedelta(days=random.randint(1, 7))
                    order_status = random.choice(["Pending", "Shipped", "Delivered", "Cancelled"])
                    order = {
                        "customer_id": customer_id,
                        "order_id": random.randint(100000, 999999),
                        "order_date": order_date.strftime("%Y-%m-%d"),
                        "ship_date": ship_date.strftime("%Y-%m-%d"),
                        "order_status": order_status,
                        "items": []
                    }
                    num_items = random.randint(1, max_items)
                    for _ in range(num_items):
                        category = random.choice(list(products_data["products"].keys()))
                        product = random.choice(products_data["products"][category])
                        brand = random.choice(product["brands"])
                        order["items"].append({
                            "category": category,
                            "product_name": product["name"],
                            "brand": brand["brand"],
                            "price": brand["price"]
                        })

                    order["items"] = json.dumps(order["items"]).decode("utf-8")
                    orders.append(order)

            # Extract column names and list of tuples
            if not orders:
                return [], []

            column_names = list(orders[0].keys())
            data_tuples = [tuple(order[col] for col in column_names) for order in orders]

            return {
                "column_names": column_names,
                "data_tuples": data_tuples,
                "orders_data": orders  # Pass orders directly
            }
        except Exception as e:
            print(f'generate_orders Unexpected error: {e}')
            return {
                "column_names": [],
                "data_tuples": [],
                "orders_data": []
            }

    @task()
    def insert_to_db(columns, data_tuples):
        try:
            created_count = len(data_tuples)
            inserted_count = batch_insert('orders', columns=columns, values=data_tuples)
            if inserted_count != created_count:
                raise Exception(
                    f"Mismatch in rows count - created: {created_count}, inserted: {inserted_count}"
                )
            print(f"Success: {inserted_count} rows inserted (out of {created_count} created).")
        except Exception as e:
            print(f"insert_to_db Unexpected error: {e}")
            raise

    @task()
    def save_to_minio(orders_data, bucket_name="my-json-storage"):
        try:
            # MinIO configuration
            s3_client = boto3.client(
                's3',

                endpoint_url="http://minio:9000",
                aws_access_key_id=os.environ.get("MINIO_ROOT_USER"),
                aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD"),
            )

            # Check if bucket exists, create if not
            try:
                s3_client.head_bucket(Bucket=bucket_name)
            except ClientError:
                print(f"Bucket '{bucket_name}' does not exist. Creating it...")
                s3_client.create_bucket(Bucket=bucket_name)

            # Generate dynamic file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_name = f"orders_{timestamp}.json"

            # Convert orders_data to JSON and upload
            json_data = json.dumps(orders_data, option=json.OPT_INDENT_2)
            s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=json_data)
            print(f"Orders uploaded to MinIO bucket '{bucket_name}' as '{object_name}'.")
        except Exception as e:
            print(f"save_to_minio Unexpected error: {e}")
            raise

    # Define task dependencies
    customer_data = data_from_mockaroo()
    product_data = get_product_from_db()
    results = generate_orders(customer_data, product_data)
    save_to_minio(results['orders_data'], bucket_name="my-json-storage")

etl_dag = data_fake_dag()
