import streamlit as st
from dotenv import load_dotenv
import os
import requests

load_dotenv()
BACKEND_ENDPOINT=f"http://{os.getenv('BACKEND_HOST')}:{os.getenv('BACKEND_PORT')}/get_plot/"

st.title("Автоматическое построение графиков")
query = st.text_input("Введите ваш запрос:")
if st.button("Построить"):
    with st.spinner('Выполняется запрос...'):
        response = requests.post(
            url=BACKEND_ENDPOINT,
            json={"text": query},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        response.close()
        if result.get("plot") is not None:
            graphic = result["plot"]
            st.image(f"data:image/png;base64,{graphic}")
        else:
            st.write("Не удалось построить график.")
