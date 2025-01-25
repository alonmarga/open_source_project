# airflow/dags/spark_dag.py
from airflow.decorators import dag
from datetime import datetime
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
)
def my_dag():
    # We rely on the AIRFLOW_CONN_MY_SPARK_CONN env var to define master="spark://spark-master:7077"
    # We'll use packages so the Airflow "driver" can also fetch these jars if needed:
    submit_job = SparkSubmitOperator(
        task_id="submit_job",
        conn_id="my_spark_conn",
        application="/opt/airflow/include/read.py",
        # Use packages instead of local jar paths to avoid "not found" on the Airflow side:
        packages="org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.504",
        conf={
            "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
            "spark.hadoop.fs.s3a.access.key": "K02e2gI7iOKwQrV6RP8j",
            "spark.hadoop.fs.s3a.secret.key": "dn2Gi8jKA9y4QLZdYiSzVXcPCNn7TFis6bhzwATi",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        },
        # Deploy in "client" mode by default. Spark standalone cluster doesn't always do python in "cluster" mode well.
        # Leave 'deploy_mode' out or set it to 'client' if you prefer:
        deploy_mode="client",
        verbose=True,
    )

    submit_job

my_dag()
