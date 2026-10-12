import streamlit as st
import pandas as pd

st.title("Diagnostyka Excel")

uploaded_file = st.file_uploader(
    "Wybierz plik XLSX",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    st.subheader("Kolumny wykryte przez Pandas")

    st.write(df.columns.tolist())

    st.subheader("Pierwsze 10 wierszy")

    st.dataframe(df.head(10))
