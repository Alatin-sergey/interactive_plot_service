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

load_dotenv()


def extract_plot_features_api(prompt: str) -> Dict[str, Any]:
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
    llm_url = f"http://{os.getenv("LLM_HOST")}:{os.getenv("LLM_PORT")}"
    try:
        template = """
        Твоя задача - извлечь ключевые элементы из запроса пользователя для построения графика.
        Определи следующие элементы запроса и верни их в формате JSON:
        1.  Тип графика (plot_type):
            *   line - для отображения динамики изменений во времени.
            *   bar - для сравнения категорий или отображения количества.
            *   scatter - для отображения взаимосвязи между двумя переменными.
            *   hist - для отображения распределения одной переменной.
            *   boxplot - для сравнения распределений нескольких групп.
            *   pie - для отображения доли каждой категории в общей сумме.
            *   null - если тип графика не определен.
        2.  Признак для оси X (x_axis):
            *   timestamp - для отображения времени.
            *   customer_id - для отображения идентификатора клиента.
            *   category - для отображения категории товара.
            *   purchase_amount - для отображения суммы покупки.
            *   is_returned - для отображения факта возврата товара.
            *   null - если признак для оси X не определен или не требуется.
        3.  Признак для оси Y (y_axis):
            *   timestamp - для отображения времени.
            *   customer_id - для отображения идентификатора клиента.
            *   category - для отображения категории товара.
            *   purchase_amount - для отображения суммы покупки.
            *   is_returned - для отображения факта возврата товара.
            *   count - для отображения количества записей.
            *   null - если признак для оси Y не определен или не требуется.
        4.  Агрегатная функция (aggregate):
            *   sum - для вычисления суммы.
            *   avg - для вычисления среднего значения.
            *   min - для вычисления минимального значения.
            *   max - для вычисления максимального значения.
            *   null - если агрегатная функция не требуется.
        5.  Фильтры (filters): JSON-объект с фильтрами для данных.
            *   category: Sport, Electronic, Home или null.
            *   is_returned: true, false или null.
            *   customer_id: целое число или null.
            *   date_from: дата в формате YYYY-MM-DD или null.
            *   date_to: дата в формате YYYY-MM-DD или null.
        Примеры:
        - Запрос: Показать распределение purchase_amount по category
          Ответ: {{"plot_type": "boxplot", "x_axis": "category", "y_axis": "purchase_amount", "aggregate": null, "filters": {{}}}}
        - Запрос: Динамика purchase_amount по времени
          Ответ: {{"plot_type": "line", "x_axis": "timestamp", "y_axis": "purchase_amount", "aggregate": null, "filters": {{}}}}
        - Запрос: Соотношение is_returned по category
          Ответ: {{"plot_type": "bar", "x_axis": "category", "y_axis": "is_returned", "aggregate": "count", "filters": {{}}}}
        - Запрос: Сколько возвратов было по каждой категории?
          Ответ: {{"plot_type": "bar", "x_axis": "category", "y_axis": "is_returned", "aggregate": "count", "filters": {{}}}}
        - Запрос: Распределение доходов
          Ответ: {{"plot_type": "hist", "x_axis": "purchase_amount", "y_axis": null, "aggregate": null, "filters": {{}}}}
        - Запрос: Средний чек для покупателя с id 123
          Ответ: {{"plot_type": "bar", "x_axis": "customer_id", "y_axis": "purchase_amount", "aggregate": "avg", "filters": {{"customer_id": 123}}}}
        - Запрос: Сумма покупок в категории Sport за последний месяц
          Ответ: {{"plot_type": "line", "x_axis": "timestamp", "y_axis": "purchase_amount", "aggregate": "sum", "filters": {{"category": "Sport", "date_from": "2024-05-24", "date_to": "2024-06-24"}}}}
        - Запрос: Сумма возвратов в категории Sport за последний месяц
          Ответ: {{"plot_type": "line", "x_axis": "timestamp", "y_axis": "is_returned", "aggregate": "sum", "filters": {{"category": "Sport", "is_returned": true, "date_from": "2024-05-24", "date_to": "2024-06-24"}}}}
        - Запрос: Какова динамика количества уникальных клиентов по времени?
          Ответ: {{"plot_type": "line", "x_axis": "timestamp", "y_axis": "customer_id", "aggregate": "count", "filters": {{}}}}
        - Запрос: Сколько дохода мы потеряли из-за возвратов?
          Ответ: {{"plot_type": "bar", "x_axis": "is_returned", "y_axis": "purchase_amount", "aggregate": "sum", "filters": {{"is_returned": true}}}}

        Дата сейчас: {date}
        Запрос пользователя: {message}

        Верни только JSON, без дополнительных слов и символов.
        """
        final_prompt = template.format(message=prompt, date=datetime.datetime.now())
        url = f"{llm_url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": final_prompt,
            "model": os.getenv("MODEL"),
            "stream": False
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()
        generated_text = response_json.get("response").strip()
        if generated_text:
            logger.info("Ответ получен")
            logger.info(f"{generated_text}")
            return json.loads(generated_text)
        else:
            logger.error(f"Ошибка: Не удалось получить словарь из ответа: {response_json}")
            return None
        
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
        select_clause += f"{json_data.get("x_axis")} AS {json_data.get("x_axis")}, {json_data.get("aggregate")}({json_data.get("y_axis")}) AS {json_data.get("y_axis")}"
    elif json_data.get("aggregate") is not None and json_data.get("y_axis") is not None:
        select_clause += f"{json_data.get("aggregate")}({json_data.get("y_axis")}) AS {json_data.get("y_axis")}"
    elif json_data.get("x_axis") is not None and json_data.get("y_axis") is not None:
        select_clause += f"{json_data.get("x_axis")} AS {json_data.get("x_axis")}, ({json_data.get("y_axis")}) AS {json_data.get("y_axis")}"
    else:
        if json_data.get("y_axis") is not None:
            select_clause += f"{json_data.get("y_axis")}"
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
        group_by_clause = f"GROUP BY {json_data.get("x_axis")}"
        order_by_clause = f"ORDER BY {json_data.get("x_axis")}"

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
            host="postgres", # Внутри контейнера docker-compose host ассоциируется с именем сервиса.
            port=5432,
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
    logger.info(f"Построение графика \n plot_type={json_data.get('plot_type')}, x_axis={json_data.get('x_axis')}, y_axis={json_data.get('y_axis')}")
    try:
        if df.empty:
            return None
        if json_data.get("plot_type") == "line":
            plt.figure(figsize=(10, 6))
            sns.lineplot(x=json_data.get("x_axis"), y=json_data.get("y_axis"), data=df)
            plt.xlabel(json_data.get("x_axis"))
            plt.ylabel(json_data.get("y_axis"))
            plt.title(f"Динамика {json_data.get('y_axis')} по {json_data.get('x_axis')}")
            plt.grid(True)

        elif json_data.get("plot_type") == "bar":
            plt.figure(figsize=(10, 6))
            sns.barplot(x=json_data.get("x_axis"), y=json_data.get("y_axis"), data=df)
            plt.xlabel(json_data.get("x_axis"))
            plt.ylabel(json_data.get("y_axis"))
            plt.title(f"Соотношение {json_data.get('y_axis')} по {json_data.get('x_axis')}")
            plt.grid(True)

        elif json_data.get("plot_type") == "hist":
            plt.figure(figsize=(10, 6))
            if json_data.get("y_axis") is None:
                sns.histplot(x=json_data.get("x_axis"), data=df, bins=30)
                plt.title(f"Распределение {json_data.get('x_axis')}")
            else:
                for category in df[json_data.get("x_axis")].unique():
                    subset = df[df[json_data.get("x_axis")] == category]
                    sns.histplot(x=json_data.get("y_axis"), data=subset, kde=True, label=category, bins=30)
                    plt.title(f"Распределение {json_data.get('y_axis')} по {json_data.get('x_axis')}")
                plt.xlabel("Purchase Amount")
                plt.ylabel("Frequency")
                plt.grid(True)
                plt.legend()

        elif json_data.get("plot_type") == "boxplot":
            plt.figure(figsize=(10, 6))
            sns.boxplot(x=json_data.get("x_axis"), y=json_data.get("y_axis"), data=df)
            plt.xlabel(json_data.get("x_axis"))
            plt.ylabel(json_data.get("y_axis"))
            plt.title(f"Распределение {json_data.get('y_axis')} по {json_data.get('x_axis')}")
            plt.grid(True)
            plt.suptitle("")
            
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode()
        return graphic
    except Exception as e:
        logger.error("Ошибка при построении графика")
        return None
