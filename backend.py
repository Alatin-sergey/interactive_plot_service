from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.llm_utils import AgentLLM
from loguru import logger
import base64
import os

app = FastAPI()
model = AgentLLM()


class Item(BaseModel):
    text: str


@app.post("/get_plot/")
async def get_plot(item: Item) -> Dict[str, str]:
    image_path = model.ask_question(item.text)
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return {"plot": encoded_string}
    
    except FileNotFoundError:
        logger.error(f"Файл не найден: {image_path}")
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при чтении файла")
    
    finally:
        try:
            os.remove(image_path)
            logger.info(f"Временный PNG-файл удален: {image_path}")
        except Exception as e:
            logger.warning(f"Не удалось удалить временный PNG-файл {image_path}: {e}")