import random
from typing import List, Tuple, Any, Union
from datetime import datetime
from sqlalchemy.engine import Engine 
from postgres_tables import SalesData, engine, Base
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_data(
        customer_id_range: int = 1000,
        categories: List[str] = ["Sport", "Electronic", "Home"],
        mean_purchase_amount: float = 5000.,
        std_purchase_amount: float = 2000.,
        is_returned_list: List[Any] = [True, False]
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
    purchase_amount = round(random.normalvariate(mean_purchase_amount, std_purchase_amount), 2)
    is_returned = random.choice(is_returned_list)
    return (timestamp, customer_id, category, purchase_amount, is_returned)


def insert_data(
        data: Union[Tuple[Any], List[Tuple[Any]]], 
        columns: List[str] = [
            "timestamp", 
            "customer_id", 
            "category", 
            "purchase_amount", 
            "is_returned",
        ],
        db_engine: Engine = engine,
        table_model: Base = SalesData,
) -> None:
    """
    Вставляет данные в базу данных PostgreSQL.
    args:
        data (Union[Tuple[Any, ...], List[Tuple[Any, ...]]]): Кортеж или список
            кортежей, представляющих данные для вставки. Каждый кортеж должен содержать
            значения для одной строки в порядке, указанном параметром `columns`.
        columns (List[str], optional): Список названий столбцов в порядке, в котором
            предоставляются значения данных. По умолчанию
            ["timestamp", "customer_id", "category", "purchase_amount", "is_returned"].
        db_engine (Engine): Объект SQLAlchemy Engine, используемый для подключения к базе данных.
        table_model (DeclarativeBase): Класс модели SQLAlchemy declarative base,
            представляющий таблицу для вставки данных.
    return:
        None
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
    except:
        raise ValueError("Ошибка движка при подключении к базе данных")
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        if isinstance(data, tuple):
            data_dict = dict(zip(columns, data))
            new_record = table_model(**data_dict)
            session.add(new_record)
            logger.info(f"Запись успешно добавлена в таблицу {table_model.__tablename__}: {new_record}")
        elif isinstance(data, list):
            records_to_insert = []
            for item in data:
                data_dict = dict(zip(columns, item))
                new_record = table_model(**data_dict)
                records_to_insert.append(new_record)
            session.add_all(records_to_insert)
            logger.info(f"{len(records_to_insert)} - количество объектов, успешно добавленых в таблицу {table_model.__tablename__}")
        else:
            raise TypeError("Данные должны быть кортежем или списком")
        session.commit()
    except Exception as e:
        session.rollback()
        raise ConnectionError(f"Error inserting data into {table_model.__tablename__}: {e}")
    finally:
        session.close()


def insert_data_task() -> None:
    """Сбор задачи для DAG. Генерирует данные и вставляет в таблицу"""
    data = generate_data()
    insert_data(data)


def insert_300_objects_task() -> None:
    """Сбор задачи для DAG. Генерирует 300 объектов и вставляет в таблицу"""
    data = []
    for _ in range(300):
        data.append(generate_data())
    insert_data(data)
