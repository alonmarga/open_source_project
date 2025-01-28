import sys
sys.path.append("/opt/airflow/include")

from common.spark_session import create_spark_session

from dotenv import load_dotenv
from pyspark.sql.functions import from_json, col, to_json
from pyspark.sql.types import ArrayType, StructType, StructField, StringType, DoubleType
import os


load_dotenv()




def read_from_minio(spark):
    print("Reading jsons")
    schema = ArrayType(StructType([
        StructField("category", StringType()),
        StructField("product_name", StringType()),
        StructField("brand", StringType()),
        StructField("price", DoubleType())
    ]))

    df = spark.read \
        .option("multiline", "true") \
        .json("s3a://my-json-storage/*.json") \
        .withColumn("items", from_json(col("items"), schema))

    print(f"Total records: {df.count()}")
    return df


def write_to_postgres(df):
    print("Writing to DB")
    df_to_write = df.withColumn("items", to_json(col("items")).cast("string"))

    df_to_write.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://postgres:5432/{os.environ.get('POSTGRES_DB')}") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "orders") \
        .option("user", os.environ.get('POSTGRES_USER')) \
        .option("password", os.environ.get('POSTGRES_PASSWORD')) \
        .option("stringtype", "unspecified") \
        .mode("append") \
        .save()
    print("Done writing to DB")


def main():
    spark = None
    try:
        spark = create_spark_session("Read Orders Job")
        df = read_from_minio(spark)
        write_to_postgres(df)
        print("Process completed successfully")
    except Exception as e:
        print(f"Error in processing: {e}")
        raise
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    main()