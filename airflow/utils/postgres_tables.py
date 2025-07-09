from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    create_engine,
)
from sqlalchemy.orm import declarative_base

engine = create_engine(f"postgresql+psycopg2://airflow:airflow@postgres/airflow") # Тут не подгружается .env
# URL копирует docker-compose AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
Base = declarative_base()


class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    customer_id = Column(String)
    category = Column(String)
    purchase_amount = Column(Float)
    is_returned = Column(Boolean)


Base.metadata.create_all(bind=engine)