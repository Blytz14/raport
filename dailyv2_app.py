import streamlit as st
import pandas as pd

st.title("Diagnostyka kolumny Data")

uploaded_file = st.file_uploader(
    "Wybierz plik XLSX",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    st.write("Typ kolumny Data:")
    st.write(df["Data"].dtype)

    st.write("Pierwsze 20 wartości:")

    st.dataframe(
        df[["Data"]].head(20)
    )
