from pyspark.sql import SparkSession
import os

def create_spark_session(app_name="PySpark Job"):
    print(f"Building Spark session for {app_name}...")
    return (SparkSession.builder
            .appName(app_name)
            .master("spark://spark-master:7077")
            .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
            .config("spark.hadoop.fs.s3a.access.key", os.environ.get('MINIO_ACCESS_KEY'))
            .config("spark.hadoop.fs.s3a.secret.key", os.environ.get('MINIO_SECRET_KEY'))
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .getOrCreate())