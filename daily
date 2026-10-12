import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="UR Insight",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 UR Insight")
st.subheader("Analiza raportów Utrzymania Ruchu")

uploaded_file = st.file_uploader(
    "Wybierz plik XLSX",
    type=["xlsx"]
)


def load_excel(file):
    xl = pd.ExcelFile(file)

    dataframes = []

    for sheet in xl.sheet_names:

        try:
            df = pd.read_excel(file, sheet_name=sheet)

            df["Arkusz"] = sheet

            dataframes.append(df)

        except Exception:
            pass

    if len(dataframes) == 0:
        return None

    return pd.concat(dataframes, ignore_index=True)


def detect_column(df, keywords):

    for col in df.columns:
        col_lower = str(col).lower()

        for keyword in keywords:
            if keyword in col_lower:
                return col

    return None


def create_summary(df):

    czas_col = detect_column(
        df,
        ["czas", "time", "min"]
    )

    maszyna_col = detect_column(
        df,
        ["maszyna", "machine"]
    )

    pracownik_col = detect_column(
        df,
        ["pracownik", "wykonał", "mechanik"]
    )

    kategoria_col = detect_column(
        df,
        ["kategoria"]
    )

    liczba_interwencji = len(df)

    laczny_czas = 0

    if czas_col:
        try:
            laczny_czas = pd.to_numeric(
                df[czas_col],
                errors="coerce"
            ).fillna(0).sum()
        except:
            pass

    godziny = int(laczny_czas // 60)
    minuty = int(laczny_czas % 60)

    top_kategoria = "Brak danych"

    if kategoria_col:
        try:
            top_kategoria = (
                df[kategoria_col]
                .astype(str)
                .value_counts()
                .head(2)
                .index
                .tolist()
            )

            top_kategoria = ", ".join(top_kategoria)
        except:
            pass

    top_maszyny = "Brak danych"

    if maszyna_col:
        try:
            top_maszyny = (
                df[maszyna_col]
                .astype(str)
                .value_counts()
                .head(3)
                .index
                .tolist()
            )

            top_maszyny = ", ".join(top_maszyny)
        except:
            pass

    top_pracownicy = "Brak danych"

    if pracownik_col:
        try:
            top_pracownicy = (
                df[pracownik_col]
                .astype(str)
                .value_counts()
                .head(5)
                .index
                .tolist()
            )

            top_pracownicy = ", ".join(top_pracownicy)
        except:
            pass

    tekst = f"""
W analizowanym okresie dział UR wykonał {liczba_interwencji} interwencji.

Łączny czas działań wyniósł {godziny} godzin i {minuty} minut.

Najwięcej zgłoszeń dotyczyło kategorii:
{top_kategoria}.

Najczęściej obsługiwane maszyny:
{top_maszyny}.

Najbardziej zaangażowani pracownicy:
{top_pracownicy}.

Zaleca się przeanalizowanie maszyn o największej liczbie zgłoszeń
i zwiększenie działań prewencyjnych.
"""

    return tekst


if uploaded_file:

    with st.spinner("Analiza raportu..."):

        df = load_excel(uploaded_file)

    if df is None:

        st.error("Nie znaleziono danych.")

    else:

        st.success("Plik został wczytany.")

        st.write("Liczba rekordów:", len(df))

        czas_col = detect_column(
            df,
            ["czas", "min"]
        )

        maszyna_col = detect_column(
            df,
            ["maszyna"]
        )

        kategoria_col = detect_column(
            df,
            ["kategoria"]
        )

        pracownik_col = detect_column(
            df,
            ["pracownik", "mechanik", "wykonał"]
        )

        mttr = 0
        laczny_czas = 0

        if czas_col:

            czas_dane = pd.to_numeric(
                df[czas_col],
                errors="coerce"
            ).fillna(0)

            laczny_czas = czas_dane.sum()
            mttr = czas_dane.mean()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Interwencje",
            len(df)
        )

        col2.metric(
            "Czas awarii [min]",
            round(laczny_czas)
        )

        col3.metric(
            "MTTR [min]",
            round(mttr, 1)
        )

        col4.metric(
            "Rekordy",
            len(df)
        )

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Dashboard",
                "Raport dzienny",
                "Raport tygodniowy",
                "Dane"
            ]
        )

        with tab1:

            if kategoria_col:

                vc = (
                    df[kategoria_col]
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )

                vc.columns = ["Kategoria", "Liczba"]

                fig = px.pie(
                    vc,
                    values="Liczba",
                    names="Kategoria",
                    title="Awarie wg kategorii"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            if maszyna_col:

                ranking = (
                    df[maszyna_col]
                    .astype(str)
                    .value_counts()
                    .head(10)
                    .reset_index()
                )

                ranking.columns = [
                    "Maszyna",
                    "Liczba"
                ]

                fig2 = px.bar(
                    ranking,
                    x="Maszyna",
                    y="Liczba",
                    title="TOP 10 maszyn"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

            if pracownik_col:

                prac = (
                    df[pracownik_col]
                    .astype(str)
                    .value_counts()
                    .head(10)
                    .reset_index()
                )

                prac.columns = [
                    "Pracownik",
                    "Liczba"
                ]

                fig3 = px.bar(
                    prac,
                    x="Pracownik",
                    y="Liczba",
                    title="Ranking pracowników"
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )

        with tab2:

            st.subheader(
                "Automatyczny raport dzienny"
            )

            st.info(
                create_summary(df)
            )

        with tab3:

            st.subheader(
                "Podsumowanie tygodniowe"
            )

            if maszyna_col:

                top10 = (
                    df[maszyna_col]
                    .astype(str)
                    .value_counts()
                    .head(10)
                )

                st.write("### TOP 10 maszyn")
                st.dataframe(top10)

            if kategoria_col:

                top_cat = (
                    df[kategoria_col]
                    .astype(str)
                    .value_counts()
                    .head(10)
                )

                st.write("### TOP 10 kategorii")
                st.dataframe(top_cat)

            if pracownik_col:

                top_emp = (
                    df[pracownik_col]
                    .astype(str)
                    .value_counts()
                    .head(10)
                )

                st.write("### Najbardziej obciążeni pracownicy")
                st.dataframe(top_emp)

        with tab4:

            st.dataframe(
                df,
                use_container_width=True
            )
