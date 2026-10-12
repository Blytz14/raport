import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="UR Insight",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 UR Insight")
st.subheader("Analiza rejestru awarii UR")

uploaded_file = st.file_uploader(
    "Wybierz rejestr awarii XLSX",
    type=["xlsx"]
)

if uploaded_file:

    # ====================================
    # WCZYTANIE PLIKU
    # ====================================

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    # ====================================
    # CZYSZCZENIE
    # ====================================

    df = df[
        df["Data"].notna()
    ]

    df = df[
        df["Maszyna-Urządzenie"].notna()
    ]

    # Data jako tekst -> data

    df["Data"] = pd.to_datetime(
        df["Data"].astype(str),
        errors="coerce"
    )

    df = df[
        df["Data"].notna()
    ]

    # ====================================
    # CZAS
    # ====================================

    def czas_na_minuty(x):

        try:

            td = pd.to_timedelta(
                str(x)
            )

            return td.total_seconds() / 60

        except:

            return 0

    df["Czas_min"] = df["Czas"].apply(
        czas_na_minuty
    )

    # ====================================
    # FILTRY
    # ====================================

    st.sidebar.header("Filtry")

    opcja = st.sidebar.selectbox(
        "Zakres",
        [
            "Cały plik",
            "Bieżący tydzień",
            "Bieżący miesiąc",
            "Własny zakres"
        ]
    )

    df_filtered = df.copy()

    dzis = pd.Timestamp.today()

    if opcja == "Bieżący tydzień":

        start = dzis - pd.Timedelta(
            days=dzis.weekday()
        )

        koniec = start + pd.Timedelta(days=6)

        df_filtered = df[
            (df["Data"] >= start)
            &
            (df["Data"] <= koniec)
        ]

    elif opcja == "Bieżący miesiąc":

        df_filtered = df[
            (df["Data"].dt.month == dzis.month)
            &
            (df["Data"].dt.year == dzis.year)
        ]

    elif opcja == "Własny zakres":

        data_od = st.sidebar.date_input(
            "Data od"
        )

        data_do = st.sidebar.date_input(
            "Data do"
        )

        df_filtered = df[
            (df["Data"] >= pd.Timestamp(data_od))
            &
            (df["Data"] <= pd.Timestamp(data_do))
        ]

    # ====================================
    # HALA
    # ====================================

    hale = sorted(
        df_filtered["Hala"]
        .astype(str)
        .unique()
    )

    wybrane_hale = st.sidebar.multiselect(
        "Hala",
        hale,
        default=hale
    )

    df_filtered = df_filtered[
        df_filtered["Hala"]
        .astype(str)
        .isin(wybrane_hale)
    ]

    # ====================================
    # ZMIANA
    # ====================================

    zmiany = sorted(
        df_filtered["Zmiana"]
        .astype(str)
        .unique()
    )

    wybrane_zmiany = st.sidebar.multiselect(
        "Zmiana",
        zmiany,
        default=zmiany
    )

    df_filtered = df_filtered[
        df_filtered["Zmiana"]
        .astype(str)
        .isin(wybrane_zmiany)
    ]

    # ====================================
    # KPI
    # ====================================

    zdarzenia = len(df_filtered)

    czas_h = round(
        df_filtered["Czas_min"].sum() / 60,
        1
    )

    mttr = round(
        df_filtered["Czas_min"].mean(),
        1
    ) if zdarzenia else 0

    maszyny = (
        df_filtered["Maszyna-Urządzenie"]
        .nunique()
    )

    przeglady = len(
        df_filtered[
            df_filtered[
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
        df_filtered[
            df_filtered[
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

    awarie = (
        zdarzenia -
        przeglady -
        zadania
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Zdarzenia", zdarzenia)
    c2.metric("Awarie", awarie)
    c3.metric("Przeglądy", przeglady)
    c4.metric("Zadania", zadania)
    c5.metric("Maszyny", maszyny)
    c6.metric("MTTR", mttr)

    # ====================================
    # RAPORT
    # ====================================

    st.divider()

    if len(df_filtered) > 0:

        top_maszyna = (
            df_filtered[
                "Maszyna-Urządzenie"
            ]
            .value_counts()
            .index[0]
        )

        st.info(
            f"""
W analizowanym okresie zarejestrowano {zdarzenia} zdarzeń.

Łączny czas działań wyniósł {czas_h} godzin.

Najczęściej obsługiwaną maszyną była:
{top_maszyna}.

Średni czas działania wyniósł
{mttr} minut.
"""
        )

    # ====================================
    # TOP MASZYNY
    # ====================================

    st.subheader("TOP 10 maszyn")

    top_maszyny = (
        df_filtered[
            "Maszyna-Urządzenie"
        ]
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
        y="Liczba",
        color="Liczba"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ====================================
    # TOP PRZYCZYNY
    # ====================================

    st.subheader("TOP przyczyn")

    top_przyczyny = (
        df_filtered[
            "Podkategoria awarii"
        ]
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

    # ====================================
    # TREND
    # ===========
