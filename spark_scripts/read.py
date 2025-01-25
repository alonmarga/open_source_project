from pyspark.sql import SparkSession

def main():
    print("hi")

    spark = None
    try:
        spark = SparkSession.builder \
            .appName("PySpark Example") \
            .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
            .config("spark.hadoop.fs.s3a.access.key", "K02e2gI7iOKwQrV6RP8j") \
            .config("spark.hadoop.fs.s3a.secret.key", "dn2Gi8jKA9y4QLZdYiSzVXcPCNn7TFis6bhzwATi") \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .getOrCreate()

        print("sparksession", spark)
        df = spark.read.csv("s3a://my-json-storage/orders_20250109_000435.json", header=True)
        df.show()

    except Exception as e:
        print(f"Error while reading the CSV file: {e}")
    finally:
        if spark is not None:
            spark.stop()

if __name__ == "__main__":
    main()