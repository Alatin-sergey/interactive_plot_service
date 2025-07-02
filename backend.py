from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from utils.data_utils import (
    generate_sql,
    generate_plot,
    get_data,
    extract_plot_features_api
)

load_dotenv()
app = FastAPI()

class Item(BaseModel):
    text: str


@app.post("/get_plot/")
async def get_plot(item: Item) -> Dict[str, str]:
    try:
        json_data = extract_plot_features_api(item.text)
        sql_query = generate_sql(json_data)
        df = get_data(sql_query)
        graphic = generate_plot(df, json_data)
        return {"plot": graphic}
    except Exception as e:
        return {"error": e}
