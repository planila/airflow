import pandas as pd
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import csv
import json
from email.policy import default
from datetime import datetime, timedelta
from airflow import DAG
from  airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pendulum

local_time = pendulum.timezone("Europe/Moscow")

name = ['SOLUSDT', '1INCHUSDT', 'SUIUSDT', 'TONUSDT', 'STRKUSDT']
days = 10
d1 = dict()

def do_task1():
    for i in name:
        def pull_tokens_csv(i, days):
            end = int(datetime.now().timestamp() * 1000)
            start = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

            url = f'https://api.binance.com/api/v3/klines'

            params = {
                'symbol': i,
                'interval': '1d',
                'startTime': start,
                'endTime': end,
                'limit': 7
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                d1[i] = data


            else:
                print(f"Ошибка: {response.status_code}")


        pull_tokens_csv(i, days)

default_args = {
    'owner': 'Danil',
    'start_date':local_time.convert(datetime(2024, 9, 28, 0, 0)),
    'retries':5
}

with DAG(
    dag_id = 'api_binance_dag1',
    default_args = default_args,
    description = 'This dag take data from api and push it in dict',
    schedule_interval = '0 12 * * *' # минуты, часы, день месяца, месяц, день недели
) as dag:
    task1 = PythonOperator(
        task_id='api_dag1',
        python_callable= do_task1,
    )




task1
