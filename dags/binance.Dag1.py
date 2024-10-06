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

token_names: list[str] = ['SOLUSDT', '1INCHUSDT', 'SUIUSDT', 'TONUSDT', 'STRKUSDT']
days: int = 10
crypto_data = dict()


def pull_tokens_csv(days: int):  #она ничего не возвращает, соответственно, тип возврата незачем указывать?

    end: int = int(datetime.now().timestamp() * 1000)
    start: int = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

    url: str = f'https://api.binance.com/api/v3/klines'

    params = {
        'interval': '1d',
        'startTime': start,
        'endTime': end,
        'limit': 7
    }

    response: str = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        crypto_data[value] = data


    else:
        print(f"Ошибка: {response.status_code}")


    #ti.xcom_push(key='my_data', value=data)


default_args = {
    'owner': 'Danil',
    'start_date':local_time.convert(datetime(2024, 9, 29, 0, 55)),
    'retries':5
}

with DAG(
    dag_id = 'api_binance_dag1',
    default_args = default_args,
    description = 'This dag take data from api and push it in dict',
    schedule_interval = '0 12 * * *' # минуты, часы, день месяца, месяц, день недели
) as dag:
    for value in token_names:
        task1 = PythonOperator(
            task_id = f'process_{value}',
            python_callable= pull_tokens_csv,
            # op_kwargs={'value': value} не понял для чего и как нужна эта штука
        )


task1




