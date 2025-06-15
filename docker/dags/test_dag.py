from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello_world():
    print("Hello from Airflow!")

with DAG(
    dag_id='test_dag',
    schedule='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["test"],
) as dag:
    task = PythonOperator(
        task_id='hello_task',
        python_callable=hello_world,
    )