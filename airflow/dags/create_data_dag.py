from airflow.decorators import dag, task
from datetime import datetime, timedelta
import orjson as json
import requests
import pandas as pd
import random
import os


from app.db import query_db

default_args = {
    'owner': 'Alon Margalit',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='Create_data',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example']
)
def data_fake_dag():
    @task()
    def data_from_mockaroo():
        try:
            url = "https://api.mockaroo.com/api/generate.json?key=82bfd910&schema=pii"
            response = requests.get(url)
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
    def get_product_file():
        try:
            airflow_home = os.getenv('AIRFLOW_HOME', '/usr/local/airflow')  # Default Airflow home path
            file_path = os.path.join(airflow_home, 'products_data.json')
            with open(file_path, 'r') as f:
                data = json.loads(f.read())
            return data
        except Exception as e:
            print(f'get_product_file Unexpected error: {e}')
            return {}

    @task()
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
                    orders.append(order)
            orders_df = pd.DataFrame(orders)
            print(orders_df)
            # return orders_df
        except Exception as e:
            print(f'generate_orders Unexpected error: {e}')
            return pd.DataFrame()

    @task()
    def insert_to_db():
        sql ='select * from dev_tg_users;'
        return query_db(sql)

    # Define task dependencies
    customer_data = data_from_mockaroo()
    product_data = get_product_file()
    generate_orders(customer_data, product_data)
    insert_to_db()

etl_dag = data_fake_dag()
