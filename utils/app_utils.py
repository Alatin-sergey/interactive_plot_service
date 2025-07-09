import os
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
url = f"http://{os.getenv('BACKEND_SERVICE')}:{os.getenv('BACKEND_PORT')}/get_plot/"

def request_to_get_plot(query: str) -> str:
    """
    Функция выполняет запрос в backend, передавая пользовательский запрос на построение графика
    args:
        query - текстовый запрос пользователя
    returns:
        str - изображение PNG в кодировке UTF-8.
    """
    logger.info(url)
    response = requests.post(
            url=url,
            json={"text": query},
            headers={"Content-Type": "application/json"}
    )
    result = response.json()
    response.close()
    if "error" in result.keys():
        raise ValueError(f"Ошибка при запросе: {result.get('error')}")
    else:
        return result.get("plot")
