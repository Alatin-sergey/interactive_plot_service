import random
from typing import List, Tuple, Any
from datetime import datetime
import os
from sqlalchemy import (
    create_engine, 
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
)


try:
    engine = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVICE')}:{os.getenv('POSTGRES_PORT')}/airflow")
    with engine.connect() as connection:
        connection.execute("SELECT 1")
except Exception as e:
    engine = None

metadata_sd = MetaData()
sales_data = Table(
    "sales_data",
    metadata_sd,
    Column("id", Integer, autoincrement=True, primary_key=True),
    Column("timestamp", DateTime, nullable=False),
    Column("customer_id", Integer, nullable=False),
    Column("category", String(50), nullable=False),
    Column("purchase_amount", Float, nullable=False),
    Column("is_returned", Boolean, nullable=False),
)


def generate_data(
        customer_id_range: int=1000,
        categories: List[str]=["Sport", "Electronic", "Home"],
        mean_purchase_amount: float=5000.,
        std_purchase_amount: float=2000.,
) -> Tuple[datetime, int, str, float, bool]:
    """
    Генерирует случайные значения в соответствии с колонками таблицы SQL
    customer_id: Случайное целое число от 0 до 999
    category: Случайный выбор из ["Sport", "Electronic", "Home"]
    purchase_amount: Случайная сумма покупки (нормальное распределение, среднее 5000, стандартное отклонение 2000), >= 100, округленная до 2 знаков
    is_returned: Случайное булево значение (True или False)

    args:
        - customer_id_range - максимальное значение id пользователя
        - categories - список категорий товаров
        - mean_purchase_amount - матожидание нормального распределения случайной генерации дохода
        - std_purchase_amount - стандартное отклонение нормального распределения случайной генерации дохода
    returns:
        List[str, float] - одну строку таблицы.
    """
    timestamp = datetime.now()
    customer_id = random.choice(range(customer_id_range))
    category = random.choice(categories)
    purchase_amount = round(max(0.1, random.normalvariate(mean_purchase_amount, std_purchase_amount)), 2)
    is_returned = random.choice([True, False])
    return (timestamp, customer_id, category, purchase_amount, is_returned)


def insert_data(
        data: Tuple[Any], 
        table_name: str="sales_data", 
        columns: List[str]=[
            "timestamp", 
            "customer_id", 
            "category", 
            "purchase_amount", 
            "is_returned"
        ],
        db_engine: create_engine = engine,
) -> None:
    """
    Вставляет данные в базу данных PostgreSQL.
    args:
        data - список значений признаков для одного объекта в базу данных
    """
    if db_engine is None:
        return
    target_table = metadata_sd.tables.get(table_name)
    if target_table is None:
        return
    if len(columns) != len(data):
        raise ValueError("Number of columns must match the number of data values.")
    insert_values = dict(zip(columns, data))
    insert_query = target_table.insert().values(insert_values)
    with db_engine.connect() as connection:
        connection.execute(insert_query)
        connection.commit()

