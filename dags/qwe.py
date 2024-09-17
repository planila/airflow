from email.policy import default
from datetime import datetime, timedelta

from airflow import DAG
from  airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import pendulum

local_time = pendulum.timezone("Europe/Berlin")

def make_greet_again():
    print('Hello world')

default_args = {
    'owner': 'dan',
    'start_date':local_time.convert(datetime(2024, 9, 18, 1, 15)),
    'retries':5
}

with DAG(
    dag_id = 'my_first_dag',
    default_args = default_args,
    description = 'This is our first dag that we..I wrote',
    schedule_interval = '15 13 * * *'
) as dag:
    task1 = PythonOperator(
        task_id='first_task',
        python_callable= make_greet_again,
    )

task1