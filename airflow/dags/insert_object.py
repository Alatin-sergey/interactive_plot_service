from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime
from airflow_utils import insert_data_task

START_DATE = datetime.datetime(2025, 6, 23)


with DAG(
    dag_id="insert_object",
    schedule_interval="*/1 * * * *",
    start_date=START_DATE,
    catchup=False,
    tags=["insert", "1_minutes", "1_object"],
) as dag:
    task1 = PythonOperator(
        task_id="insert_data_task",
        python_callable=insert_data_task,
    )
