from pyspark.sql import SparkSession
from dotenv import load_dotenv
from pyspark.sql.functions import from_json, col, to_json

from pyspark.sql.types import ArrayType, StructType, StructField, StringType, DoubleType

import os

load_dotenv()


def main():
    spark = None
    try:
        spark = (SparkSession.builder \
                 .appName("PySpark Example") \
                 .master("spark://spark-master:7077") \
                 .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
                 .config("spark.hadoop.fs.s3a.access.key", "K02e2gI7iOKwQrV6RP8j") \
                 .config("spark.hadoop.fs.s3a.secret.key", "dn2Gi8jKA9y4QLZdYiSzVXcPCNn7TFis6bhzwATi") \
                 .config("spark.hadoop.fs.s3a.path.style.access", "true") \
                 .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
                 .getOrCreate())

        df = spark.read \
            .option("multiline", "true") \
            .json("s3a://my-json-storage/*.json") \
            .withColumn(
            "items",
            from_json(
                col("items"),
                ArrayType(StructType([
                    StructField("category", StringType()),
                    StructField("product_name", StringType()),
                    StructField("brand", StringType()),
                    StructField("price", DoubleType())
                ]))
            )
        )

        print(f"Total records: {df.count()}")
        df.show()

        df_to_write = df.withColumn("items", to_json(col("items")).cast("string"))

        df_to_write.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://postgres:5432/mydatabase") \
            .option("driver", "org.postgresql.Driver") \
            .option("dbtable", "orders") \
            .option("user", "myuser") \
            .option("password", "mypassword") \
            .option("stringtype", "unspecified") \
            .mode("append") \
            .save()


    except Exception as e:
        print(f"Error reading orders: {e}")
        raise
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    main()