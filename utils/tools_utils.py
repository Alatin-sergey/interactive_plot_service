import os
from dotenv import load_dotenv
import psycopg2
from loguru import logger
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
from plot_utils import (
    line_plot,
    bar_plot,
    hist_plot,
    box_plot,
    pie_plot,
)

load_dotenv()


def get_data_from_sql(sql_query: str) -> pd.DataFrame:
    """
    Выполняет SQL-запрос к базе данных PostgreSQL и возвращает результат в виде файла формата CSV.

    Args:
        sql_query (str): SQL-запрос, который необходимо выполнить.

    Returns:
        file CSV: временный CSV файл с выгруженными данными.
    """
    logger.info("Отправка запроса в базу данных")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_SERVICE"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        logger.info("Датафрейм успешно получен")
        df = pd.DataFrame(data, columns=column_names)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".csv") as tmpfile:
            csv_data = df.to_csv(index=False)
            tmpfile.write(csv_data)
            file_path = tmpfile.name
            logger.info(f"CSV данные сохранены во временный файл: {file_path}")
        return file_path
    except Exception:
        logger.error("Ошибка выгрузки датафрейма из базы данных")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def chart_building(csv_file_path: str, plot_type: str, x_axis: str, y_axis: str) -> str:
    """
    Генерирует график на основе данных и типа графика.

    args:
        df (str): DataFrame с данными для построения графика.
        plot_type (str): Тип графика ("line", "bar", "hist", "boxplot").
        x_axis (str): Название столбца для оси X.
        y_axis (str): Название столбца для оси Y.

    returns:
        str or None: Строка, представляющая PNG изображение графика, закодированное в Base64 (UTF-8).
                    Возвращает None, если не удалось построить график.
    """
    try:
        plot_dict = {
            "line": line_plot,
            "bar": bar_plot,
            "hist": hist_plot,
            "boxplot": box_plot,
            "pie": pie_plot,
        }
        logger.info(f"Построение графика: plot_type={plot_type}, x_axis={x_axis}, y_axis={y_axis}")
        df = pd.read_csv(csv_file_path)
        if df.empty:
            logger.warning('CSV-файл пустой или его не существует. Невозможно создать график.')
            raise ValueError('CSV-файл пустой или его не существует. Невозможно создать график.')
        plot_dict[plot_type](
            df,
            x_axis,
            y_axis,
        )
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                plt.savefig(tmpfile.name, format="png")
                logger.info(f"PNG график сохранен во временный файл: {tmpfile.name}")
                plt.close()
        return tmpfile.name
    finally:
        try:
            os.remove(csv_file_path)
            logger.info(f"Временный CSV файл удален: {csv_file_path}")
        except Exception as e:
            logger.warning(f"Не удалось удалить временный CSV-файл {csv_file_path}: {e}")
