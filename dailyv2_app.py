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

    # ---------------------------------
    # WCZYTANIE XLSX
    # ---------------------------------

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # ---------------------------------
    # CZYSZCZENIE
    # ---------------------------------

    if "Data" in df.columns:
        df = df[df["Data"].notna()]

    if "Maszyna-Urządzenie" in df.columns:
        df = df[df["Maszyna-Urządzenie"].notna()]

    # Bezpieczna konwersja dat

    df["Data"] = pd.to_datetime(
        df["Data"],
        errors="coerce",
        format="mixed"
    )

    df = df[df["Data"].notna()]

    # ---------------------------------
    # CZAS
    # ---------------------------------

    def czas_na_minuty(wartosc):

        try:

            td = pd.to_timedelta(
                str(wartosc)
            )

            return td.total_seconds() / 60

        except:

            return 0

    df["Czas_min"] = (
        df["Czas"]
        .astype(str)
        .apply(czas_na_minuty)
    )

    # ---------------------------------
    # FILTRY
    # ---------------------------------

    st.sidebar.header("Filtry")

    okres = st.sidebar.selectbox(
        "Zakres",
        [
            "Cały plik",
            "Bieżący tydzień",
            "Bieżący miesiąc",
            "Własny zakres"
        ]
    )

    if okres == "Cały plik":

        df_okres = df.copy()

    elif okres == "Bieżący tydzień":

        today = pd.Timestamp.now()

        start = today - pd.Timedelta(
            days=today.weekday()
        )

        koniec = start + pd.Timedelta(days=6)

        df_okres = df[
            (df["Data"] >= start)
            &
            (df["Data"] <= koniec)
        ]

    elif okres == "Bieżący miesiąc":

        today = pd.Timestamp.now()

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

    # ---------------------------------
    # HALA
    # ---------------------------------

    hale = sorted(
        df_okres["Hala"]
        .astype(str)
        .unique()
    )

    hale_wybrane = st.sidebar.multiselect(
        "Hala",
        hale,
        default=hale
    )

    df_okres = df_okres[
        df_okres["Hala"]
        .astype(str)
        .isin(hale_wybrane)
    ]

    # ---------------------------------
    # ZMIANY
    # ---------------------------------

    zmiany = sorted(
        df_okres["Zmiana"]
        .astype(str)
        .unique()
    )

    zmiany_wybrane = st.sidebar.multiselect(
        "Zmiana",
        zmiany,
        default=zmiany
    )

    df_okres = df_okres[
        df_okres["Zmiana"]
        .astype(str)
        .isin(zmiany_wybrane)
    ]

    # ---------------------------------
    # KPI
    # ---------------------------------

    liczba_zdarzen = len(df_okres)

    liczba_maszyn = (
        df_okres["Maszyna-Urządzenie"]
        .nunique()
    )

    czas_min = (
        df_okres["Czas_min"]
        .sum()
    )

    czas_h = round(
        czas_min / 60,
        1
    )

    mttr = round(
        df_okres["Czas_min"].mean(),
        1
    ) if liczba_zdarzen > 0 else 0

    przeglady = len(
        df_okres[
            df_okres[
                "Podkategoria awarii"
            ]
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
            df_okres[
                "Podkategoria awarii"
            ]
            .astype(str)
            .str.contains(
                "zadanie",
                case=False,
                na=False
            )
        ]
    )

    awarie = max(
        liczba_zdarzen - przeglady - zadania,
        0
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Zdarzenia", liczba_zdarzen)
    c2.metric("Awarie", awarie)
    c3.metric("Przeglądy", przeglady)
    c4.metric("Zadania", zadania)
    c5.metric("Czas [h]", czas_h)
    c6.metric("MTTR [min]", mttr)

    # ---------------------------------
    # TOP MASZYNY
    # ---------------------------------

    st.subheader("TOP 10 maszyn")

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

    fig = px.bar(
        top_maszyny,
        x="Maszyna",
        y="Liczba"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------
    # TREND
    # ---------------------------------

    st.subheader("Trend zgłoszeń")

    trend = (
        df_okres
        .groupby(df_okres["Data"].dt.date)
        .size()
        .reset_index(name="Liczba")
    )

    fig2 = px.line(
        trend,
        x="Data",
        y="Liczba",
        markers=True
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ---------------------------------
    # DANE
    # ---------------------------------

    with st.expander("Pokaż dane"):

        st.dataframe(
            df_okres,
            use_container_width=True
        )
