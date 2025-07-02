from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime
from airflow_utils import (
    generate_data, 
    insert_data,
)


def insert_data_task() -> None:
    """Сбор задачи для DAG. Генерирует данные и вставляет в таблицу"""
    data = generate_data()
    insert_data(data)


def insert_300_objects_task() -> None:
    """Сбор задачи для DAG. Генерирует 300 объектов и вставляет в таблицу"""
    data = []
    [data.append(generate_data()) for _ in range(300)]
    insert_data(data)


with DAG(
    dag_id="data_insert",
    schedule_interval="*/5 * * * *",
    start_date=datetime.datetime(2025, 6, 23),
    catchup=False,
    tags=["data", "insert", "5_minutes"],
) as dag:
    task1 = PythonOperator(
        task_id="insert_data_task",
        python_callable=insert_data_task,
    )


with DAG(
    dag_id="data_insert_300_objects",
    start_date=datetime.datetime(2025, 6, 23),
    schedule_interval=None,
    catchup=False,
    tags=["interactive", "data", "300 objects"]
) as dag:
    task = PythonOperator(
        task_id=f"insert_300_objects_task",
        python_callable=insert_300_objects_task,
    )
