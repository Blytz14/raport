import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="UR Insight",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Analiza rejestru awarii UR")

uploaded_file = st.file_uploader(
    "Wybierz rejestr awarii XLSX",
    type=["xlsx"]
)

if uploaded_file:

    # =====================================
    # WCZYTANIE EXCELA
    # =====================================

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # =====================================
    # CZYSZCZENIE DANYCH
    # =====================================

    df = df.dropna(
        subset=["Data"]
    )

    df = df[
        df["Maszyna-Urządzenie"].notna()
    ]

    df["Data"] = pd.to_datetime(
        df["Data"],
        errors="coerce"
    )

    # =====================================
    # CZAS -> MINUTY
    # =====================================

    def czas_na_minuty(x):

        try:

            td = pd.to_timedelta(
                str(x)
            )

            return td.total_seconds() / 60

        except:

            return 0

    df["Czas_min"] = (
        df["Czas"]
        .astype(str)
        .apply(czas_na_minuty)
    )

    # =====================================
    # FILTRY
    # =====================================

    st.sidebar.header("Filtry")

    today = pd.Timestamp.today()

    zakres = st.sidebar.selectbox(
        "Zakres czasu",
        [
            "Cały plik",
            "Dzisiaj",
            "Bieżący tydzień",
            "Bieżący miesiąc",
            "Własny zakres"
        ]
    )

    if zakres == "Cały plik":

        df_okres = df.copy()

    elif zakres == "Dzisiaj":

        df_okres = df[
            df["Data"].dt.date ==
            today.date()
        ]

    elif zakres == "Bieżący tydzień":

        start = today - pd.Timedelta(
            days=today.weekday()
        )

        stop = start + pd.Timedelta(days=6)

        df_okres = df[
            (df["Data"] >= start)
            &
            (df["Data"] <= stop)
        ]

    elif zakres == "Bieżący miesiąc":

        df_okres = df[
            (df["Data"].dt.month == today.month)
            &
            (df["Data"].dt.year == today.year)
        ]

    else:

        data_od = st.sidebar.date_input(
            "Data od"
        )

        data_do = st.sidebar.date_input(
            "Data do"
        )

        df_okres = df[
            (df["Data"] >= pd.Timestamp(data_od))
            &
            (df["Data"] <= pd.Timestamp(data_do))
        ]

    # =====================================
    # FILTR HALI
    # =====================================

    hale = sorted(
        df_okres["Hala"]
        .dropna()
        .astype(str)
        .unique()
    )

    wybrane_hale = st.sidebar.multiselect(
        "Hala",
        hale,
        default=hale
    )

    df_okres = df_okres[
        df_okres["Hala"]
        .astype(str)
        .isin(wybrane_hale)
    ]

    # =====================================
    # FILTR ZMIANY
    # =====================================

    zmiany = sorted(
        df_okres["Zmiana"]
        .dropna()
        .astype(str)
        .unique()
    )

    wybrane_zmiany = st.sidebar.multiselect(
        "Zmiana",
        zmiany,
        default=zmiany
    )

    df_okres = df_okres[
        df_okres["Zmiana"]
        .astype(str)
        .isin(wybrane_zmiany)
    ]

    # =====================================
    # KPI
    # =====================================

    liczba_zdarzen = len(df_okres)

    liczba_maszyn = (
        df_okres["Maszyna-Urządzenie"]
        .nunique()
    )

    laczny_czas_min = (
        df_okres["Czas_min"]
        .sum()
    )

    laczny_czas_h = round(
        laczny_czas_min / 60,
        1
    )

    mttr = round(
        df_okres["Czas_min"].mean(),
        1
    )

    przeglady = len(
        df_okres[
            df_okres["Podkategoria awarii"]
            .astype(str)
            .str.contains(
                "przegl",
                case=False,
                na=False
            )
        ]
    )

    zadania = len(
        df_okres[
            df_okres["Podkategoria awarii"]
            .astype(str)
            .str.contains(
                "zadanie",
                case=False,
                na=False
            )
        ]
    )

    awarie = (
        liczba_zdarzen
        - przeglady
        - zadania
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Zdarzenia",
        liczba_zdarzen
    )

    c2.metric(
        "Awarie",
        awarie
    )

    c3.metric(
        "Przeglądy",
        przeglady
    )

    c4.metric(
        "Zadania",
        zadania
    )

    c5.metric(
        "Czas [h]",
        laczny_czas_h
    )

    c6.metric(
        "MTTR [min]",
        mttr
    )

    st.divider()

    # =====================================
    # KOMENTARZ
    # =====================================

    if len(df_okres) > 0:

        top_maszyna = (
            df_okres["Maszyna-Urządzenie"]
            .value_counts()
            .index[0]
        )

        top_przyczyna = (
            df_okres["Podkategoria awarii"]
            .fillna("Brak")
            .value_counts()
            .index[0]
        )

        st.info(
            f"""
W analizowanym okresie zarejestrowano
{liczba_zdarzen} zdarzeń.

Łączny czas działań wyniósł
{laczny_czas_h} godzin.

Średni czas interwencji MTTR wyniósł
{mttr} minut.

Najwięcej wpisów dotyczyło maszyny:
{top_maszyna}.

Najczęściej występująca podkategoria:
{top_przyczyna}.
"""
        )

    # =====================================
    # TABS
    # =====================================

    dashboard, pracownicy, dane = st.tabs(
        [
            "Dashboard",
            "Pracownicy",
            "Dane"
        ]
    )

    with dashboard:

        st.subheader(
            "TOP 10 maszyn"
        )

        top_maszyny = (
            df_okres["Maszyna-Urządzenie"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_maszyny.columns = [
            "Maszyna",
            "Liczba"
        ]

        fig1 = px.bar(
            top_maszyny,
            x="Maszyna",
            y="Liczba"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.subheader(
            "TOP przyczyn"
        )

        top_przyczyny = (
            df_okres["Podkategoria awarii"]
            .fillna("Brak")
            .value_counts()
            .head(10)
            .reset_index()
        )

        top_przyczyny.columns = [
            "Przyczyna",
            "Liczba"
        ]

        fig2 = px.bar(
            top_przyczyny,
            x="Przyczyna",
            y="Liczba"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.subheader(
            "Trend zgłoszeń"
        )

        trend = (
            df_okres
            .groupby(
                df_okres["Data"].dt.date
            )
            .size()
            .reset_index(name="Liczba")
        )

        fig3 = px.line(
            trend,
            x="Data",
            y="Liczba",
            markers=True
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    with pracownicy:

        lista_osob = []

        for wpis in df_okres[
            "Osoba usuwająca postój, awarię"
        ].dropna():

            osoby = (
                str(wpis)
                .replace(",", "\n")
                .split("\n")
            )

            for osoba in osoby:

                osoba = osoba.strip()

                if osoba:

                    lista_osob.append(
                        osoba
                    )

        if len(lista_osob) > 0:

            ranking = (
                pd.Series(lista_osob)
                .value_counts()
                .head(20)
            )

            st.bar_chart(ranking)

            st.dataframe(
                ranking.rename(
                    "Ilość zdarzeń"
                )
            )

    with dane:

        st.dataframe(
            df_okres,
            use_container_width=True
        )
