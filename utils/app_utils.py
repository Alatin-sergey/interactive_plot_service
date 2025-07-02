import os
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

def req_get_plot(query: str) -> str:
    """
    Функция выполняет запрос в backend, передавая пользовательский запрос на построение графика
    args:
        query - текстовый запрос пользователя
    returns:
        str - изображение PNG в кодировке UTF-8.
    """

    logger.info(f"http://{os.getenv('BACKEND_SERVICE')}:{os.getenv('BACKEND_PORT')}/get_plot/")
    response = requests.post(
            url=f"http://{os.getenv('BACKEND_SERVICE')}:{os.getenv('BACKEND_PORT')}/get_plot/",
            json={"text": query},
            headers={"Content-Type": "application/json"}
    )
    result = response.json()
    response.close()
    return result.get("plot")
