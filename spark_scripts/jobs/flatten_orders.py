import sys

sys.path.append("/opt/airflow/include")

from common.spark_session import create_spark_session
from pyspark.sql.functions import explode, col, from_json
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, DoubleType
import os
from dotenv import load_dotenv

load_dotenv()


def get_items_schema():
    return ArrayType(StructType([
        StructField("category", StringType()),
        StructField("product_name", StringType()),
        StructField("brand", StringType()),
        StructField("price", DoubleType())
    ]))


def read_from_postgres(spark):
    print("Reading from orders table")

    orders_df = spark.read \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://postgres:5432/{os.environ.get('POSTGRES_DB')}") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", os.environ.get('DB_DEV_TABLE_ORDERS')) \
        .option("user", os.environ.get('POSTGRES_USER')) \
        .option("password", os.environ.get('POSTGRES_PASSWORD')) \
        .load()

    return orders_df


def flatten_orders(df):
    print("Flattening orders data")

    # Parse JSON string into array and then explode
    items_schema = get_items_schema()

    flattened_df = df.select(
        col("internal_order_id").cast("string"),  # Cast UUID to string for processing
        col("order_id"),
        col("customer_id"),
        col("order_date"),
        col("ship_date"),
        col("order_status"),
        explode(from_json(col("items"), items_schema)).alias("item")
    ).select(
        col("internal_order_id"),
        col("order_id"),
        col("customer_id"),
        col("order_date"),
        col("ship_date"),
        col("order_status"),
        col("item.category"),
        col("item.product_name"),
        col("item.brand"),
        col("item.price")
    )

    return flattened_df


def write_to_postgres(df):
    print("Writing flattened data to dev_flat_items table")

    # Properties to handle UUID type
    postgres_properties = {
        "driver": "org.postgresql.Driver",
        "url": f"jdbc:postgresql://postgres:5432/{os.environ.get('POSTGRES_DB')}",
        "user": os.environ.get('POSTGRES_USER'),
        "password": os.environ.get('POSTGRES_PASSWORD'),
        "stringtype": "unspecified",
        "batchsize": "1000",
        # Map internal_order_id to UUID type
        "createTableColumnTypes": "internal_order_id UUID"
    }

    df.write \
        .jdbc(
        url=postgres_properties["url"],
        table=os.environ.get('DB_DEV_TABLE_FLAT_ORDERS'),
        mode="append",
        properties=postgres_properties
    )

    print("Successfully written to dev_flat_items table")


def main():
    spark = None
    try:
        spark = create_spark_session("Flatten Orders Job")

        # Read orders data
        orders_df = read_from_postgres(spark)

        # Flatten the orders
        flattened_df = flatten_orders(orders_df)

        # Write results back to postgres
        write_to_postgres(flattened_df)

        print("Process completed successfully")
    except Exception as e:
        print(f"Error in processing: {e}")
        raise
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    main()