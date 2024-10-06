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

def processing_data(list_from_previous_task: list[list[str]]):
    for key, value_list in list_from_previous_task.items():  # проходимся по ключу-значению словаря

        dict_puller = []

        for i in value_list:  # идем уже по элементам (спискам) списка - значению словаря

            close_time = datetime.fromtimestamp(i[0] / 1000).strftime("%d.%m.%Y, %H:%M:%S")
            close_price = float(i[4])
            dict_puller.append((close_time, close_price))

            df = pd.DataFrame(dict_puller, columns=['Date', 'Close Price'])

            df.to_csv(f'{key}.csv', index=False, header=False)

            x = []
            y = []

        with open(f'{key}.csv', 'r') as datafile:
            plotting = csv.reader(datafile, delimiter=',')

            for rows in plotting:
                x.append(rows[0][:5])
                y.append(float(rows[1]))

        plt.plot(x, y)
        plt.title(f'{key}')
        plt.xlabel('Дата')
        plt.ylabel('Цена')
        plt.show()

default_args = {
    'owner': 'Danil',
    'start_date':local_time.convert(datetime(2024, 9, 29, 0, 55)),
    'retries':5
}

with DAG(
    dag_id = 'api_binance_dag2',
    default_args = default_args,
    description = 'This dag processes values from the first dag',
    schedule_interval = '0 12 * * *' # минуты, часы, день месяца, месяц, день недели
) as dag:
    task2 = PythonOperator(
        task_id ='data_prepare',
        python_callable= processing_data,
    )


task2