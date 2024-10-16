
import pandas as pd
import requests
from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

local_time = pendulum.timezone("Europe/Moscow")

token_names = ['SOLUSDT', '1INCHUSDT', 'SUIUSDT', 'TONUSDT', 'STRKUSDT']
days: int = 10

def pull_tokens_csv(days, value, ti):
    end: int = int(datetime.now().timestamp() * 1000)
    start: int = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

    url: str = 'https://api.binance.com/api/v3/klines'

    params = {
        'symbol': value,
        'interval': '1d',
        'startTime': start,
        'endTime': end,
        'limit': 7
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        symbol = value[:-4]
        ti.xcom_push(key=symbol, value=data)
        print(f"Pushed to XCom: Key: {symbol}, Value: {data}")
    else:
        print(f"Ошибка: {response.status_code}")

def push_from_xcom_to_df(ti):
    df_token = {}
    for value in token_names:
        symbol = value[:-4]
        data = ti.xcom_pull(key=symbol, task_ids=symbol)
        if data is not None:
            df_token[symbol] = data

    if df_token:  # Only proceed if there is data
        all_data = []
        for symbol, data in df_token.items():
            df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
            df['Symbol'] = symbol  # добавляем колонку с символом
            all_data.append(df)

        final_df = pd.concat(all_data, ignore_index=True)
        print(final_df)
    else:
        print("Нет данных для построения DataFrame")

default_args = {
    'owner': 'Danil',
    'start_date': local_time.convert(datetime(2024, 9, 29, 0, 55)),
    'retries': 5
}

with DAG(
    dag_id='api_binance_dag1',
    default_args=default_args,
    description='This dag takes data from API and pushes it into dict',
    schedule_interval='0 12 * * *'
) as dag:

    # Список для хранения задач
    tasks = []

    for value in token_names:
        task = PythonOperator(
            task_id=value[:-4],  # Убедитесь, что task_id уникален
            python_callable=pull_tokens_csv,
            op_kwargs={'days': days, 'value': value},
            provide_context=True
        )
        tasks.append(task)

    union_data = PythonOperator(
        task_id='union_data_to_df',
        python_callable=push_from_xcom_to_df,
        provide_context=True
    )

    # Связываем каждую задачу с union_data
    for task in tasks:
        task >> union_data  # Каждую задачу связываем с union_data
