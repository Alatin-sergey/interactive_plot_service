import random
from typing import List, Any
from airflow.hooks.base import BaseHook
import psycopg2
import datetime


def generate_data() -> List[Any]:
    """
    Генерирует случайные значения в соответствии с колонками таблицы SQL
    customer_id: Случайное целое число от 0 до 999
    category: Случайный выбор из ["Sport", "Electronic", "Home"]
    purchase_amount: Случайная сумма покупки (нормальное распределение, среднее 5000, стандартное отклонение 2000), >= 100, округленная до 2 знаков
    is_returned: Случайное булево значение (True или False)

    returns:
        List[str, float] - одну строку таблицы.
    """
    timestamp = datetime.datetime.now()
    customer_id = random.choice(range(1000))
    category = random.choice(["Sport", "Electronic", "Home"])
    purchase_amount = round(max(100, random.normalvariate(5000, 2000)), 2)
    is_returned = random.choice([True, False])
    return [timestamp, customer_id, category, purchase_amount, is_returned]


def insert_data(data: List[Any]) -> None:
    """
    Вставляет данные в базу данных PostgreSQL.
    args:
        data - список значений признаков для одного объекта в базу данных
    """
    try:
        conn_id = "postgres_connection"
        conn_data = BaseHook.get_connection(conn_id)

        conn = psycopg2.connect(
            host=conn_data.host,
            port=conn_data.port,
            dbname=conn_data.schema,
            user=conn_data.login,
            password=conn_data.password
        )
        cursor = conn.cursor()
        sql_query = """
            INSERT INTO sales_data (timestamp, customer_id, category, purchase_amount, is_returned)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(sql_query, data)
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
