from airflow.decorators import dag, task
from datetime import datetime, timedelta
from typing import Dict
import orjson
import requests

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


@dag(
    dag_id='example_dag',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example']
)
def example_etl_dag():
    @task()
    def data_from_mockaroo():
        # URL של Mockaroo API (תעדכן עם המפתח שלך וההגדרות)
        url = "https://api.mockaroo.com/api/generate.json?key=82bfd910&schema=pii"
        # קריאה ל-API
        response = requests.get(url)
        data = response.json()

        # המרה ל-DataFrame
        print(data)

    data_from_mockaroo()


# Instantiate the DAG
example_dag = example_etl_dag()