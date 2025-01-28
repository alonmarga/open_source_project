
import logging

from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
)
def my_dag():

    @task
    def log_start():
        logging.info("Before spark submit")

    @task(trigger_rule='all_success')
    def log_end():
        logging.info("After spark submit")

    start = log_start()

    submit_job = SparkSubmitOperator(
        task_id="submit_job",
        conn_id="my_spark_conn",
        application="/opt/airflow/include/jobs/read_and_write.py",
        packages='org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.504,org.postgresql:postgresql:42.7.1',
        deploy_mode="client",
        verbose=True,
    )
    end = log_end()

    # Define task dependencies
    start >> submit_job >> end

my_dag()