from typing import Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os
import io
from dotenv import load_dotenv
import datetime
import json
import psycopg2
import base64
from loguru import logger

from plot_utils import (
    line_plot,
    bar_plot,
    hist_plot,
    box_plot,
)

load_dotenv()
with open("prompt_for_extract_features.txt", "r", encoding="utf-8") as f:
    template = f.read()


def extract_plot_features_api(prompt: str, template: str=template) -> Dict[str, Any]:
    """
    Выполняет запрос к сервису LLM по API.
    args:
        prompt - запрос пользователя на построение графика
        model - имя модели в сервисе Ollama. Подтягивается из файла .env
        llm_url - ссылка на сервис LLM внутри контейнера Docker

    returns:
        generated_text - сгенерированный json в формате dict
    """
    logger.info("Отправка запроса в LLM")
    llm_url = f"http://{os.getenv('LLM_SERVICE')}:{os.getenv('LLM_PORT')}"
    try:
        final_prompt = template.format(message=prompt, date=datetime.datetime.now())
        url = f"{llm_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": final_prompt,
            "model": os.getenv("MODEL", "mistral"),
            "stream": False,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()
        generated_text = response_json.get("response").strip()
        logger.info("Ответ получен")
        logger.info(f"{generated_text}")
        return json.loads(generated_text)
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при вызове Ollama API: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при разборе JSON ответа {generated_text}: {e}")
        return None


def generate_sql(json_data: Dict[str, Any]) -> str:
    """Генерирует SQL-запрос на основе JSON.
    args:
        json_data - сгенерированный json

    returns:
        sql_query - сформированный SQL-запрос в формате многострочного текста.
    """
    logger.info("Формирование SQL-запроса")
    select_clause = ""
    group_by_clause = ""
    where_clause = ""
    order_by_clause = ""

    if json_data.get("aggregate") is not None and json_data.get("y_axis") is not None and json_data.get("x_axis") is not None:
        select_clause += f"{json_data.get('x_axis')} AS {json_data.get('x_axis')}, {json_data.get('aggregate')}({json_data.get('y_axis')}) AS {json_data.get('y_axis')}"
    elif json_data.get('aggregate') is not None and json_data.get('y_axis') is not None:
        select_clause += f"{json_data.get('aggregate')}({json_data.get('y_axis')}) AS {json_data.get('y_axis')}"
    elif json_data.get('x_axis') is not None and json_data.get('y_axis') is not None:
        select_clause += f"{json_data.get('x_axis')} AS {json_data.get('x_axis')}, ({json_data.get('y_axis')}) AS {json_data.get('y_axis')}"
    else:
        if json_data.get("y_axis") is not None:
            select_clause += f"{json_data.get('y_axis')}"
        else:
            select_clause = json_data.get("x_axis") if json_data.get("x_axis") is not None else "*"

    from_clause = "FROM sales_data"

    where_conditions = []
    for key, value in json_data.get("filters", {}).items():
        if value is not None:
            if key == "date_from":
                where_conditions.append(f"timestamp >= '{value}'")
            elif key == "date_to":
                where_conditions.append(f"timestamp <= '{value}'")
            elif isinstance(value, str):
                where_conditions.append(f"{key} = '{value}'")
            else:
                where_conditions.append(f"{key} = {value}")
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    
    if json_data.get("x_axis") and json_data.get("plot_type") != "hist":
        group_by_clause = f"GROUP BY {json_data.get('x_axis')}"
        order_by_clause = f"ORDER BY {json_data.get('x_axis')}"

    sql_query = f"""
        SELECT {select_clause}
        {from_clause}
        {where_clause}
        {group_by_clause}
        {order_by_clause}
    """
    logger.info(f"SQL-запрос сформирован: \n{sql_query}")
    return sql_query


def get_data(sql_query: str) -> pd.DataFrame:
    """
    Выполняет SQL-запрос к базе данных PostgreSQL и возвращает результат в виде Pandas DataFrame.

    Args:
        sql_query (str): SQL-запрос, который необходимо выполнить.

    Returns:
        pd.DataFrame or None: Pandas DataFrame с результатами запроса, если запрос выполнен успешно. 
                              Возвращает None, если произошла ошибка при подключении к базе данных, 
                              выполнении запроса или обработке результатов.
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
        return pd.DataFrame(data, columns=column_names)
    except Exception:
        logger.error("Ошибка выгрузки датафрейма из базы данных")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def generate_plot(df: pd.DataFrame, json_data: Dict[str, Any]) -> str:
    """
    Генерирует график на основе данных и типа графика.

    args:
        df (pd.DataFrame): DataFrame с данными для построения графика.
        plot_type (str): Тип графика ("line", "bar", "hist", "boxplot").
        x_axis (str): Название столбца для оси X.
        y_axis (str): Название столбца для оси Y.

    returns:
        str or None: Строка, представляющая PNG изображение графика, закодированное в Base64 (UTF-8).
                    Возвращает None, если не удалось построить график.
    """
    plot_dict = {
        "line": line_plot,
        "bar": bar_plot,
        "hist": hist_plot,
        "boxplot": box_plot
    }
    logger.info(f"Построение графика \n plot_type={json_data.get('plot_type')}, x_axis={json_data.get('x_axis')}, y_axis={json_data.get('y_axis')}")
    try:
        if df.empty:
            return None
        plot_dict[json_data.get("plot_type")](
            df,
            json_data.get("x_axis"),
            json_data.get("y_axis")
        )
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode()
        return graphic
    except Exception as e:
        logger.error("Ошибка при построении графика")
        return None
