import streamlit as st
from utils.app_utils import req_get_plot
from dotenv import load_dotenv

load_dotenv()

st.title("Автоматическое построение графиков")
query = st.text_input("Введите ваш запрос:")
if st.button("Построить"):
    with st.spinner('Выполняется запрос...'):
        plot = req_get_plot(query)
        if plot is not None:
            st.image(f"data:image/png;base64,{plot}")
        else:
            st.write("Не удалось построить график.")
