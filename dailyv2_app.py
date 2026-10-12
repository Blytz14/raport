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

    # =============================
    # WCZYTANIE PLIKU
    # =============================

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    # =============================
    # CZYSZCZENIE
    # =============================

    df = df[df["Data"].notna()]

    if "Maszyna-Urządzenie" in df.columns:
        df = df[df["Maszyna-Urządzenie"].notna()]

    df["Data"] = pd.to_datetime(
        df["Data"].astype(str),
        errors="coerce"
    )

    df = df[df["Data"].notna()]

    # =============================
    # NORMALIZACJA KATEGORII
    # =============================

    df["Kategoria awarii"] = (
        df["Kategoria awarii"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Podkategoria awarii"] = (
        df["Podkategoria awarii"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # =============================
    # CZAS
    # =============================

    def czas_na_minuty(val):

        try:
            td = pd.to_timedelta(str(val))
            return td.total_seconds() / 60
        except:
            return 0

    df["Czas_min"] = (
        df["Czas"]
        .apply(czas_na_minuty)
    )

    # =============================
    # FILTRY
    # =============================

    st.sidebar.header("Filtry")

    okres = st.sidebar.selectbox(
        "Zakres danych",
        [
            "Cały plik",
            "Bieżący tydzień",
            "Bieżący miesiąc",
            "Własny zakres"
        ]
    )

    df_filtered = df.copy()

    today = pd.Timestamp.today()

    if okres == "Bieżący tydzień":

        start = today - pd.Timedelta(
            days=today.weekday()
        )

        stop = start + pd.Timedelta(days=6)

        df_filtered = df[
            (df["Data"] >= start)
            &
            (df["Data"] <= stop)
        ]

    elif okres == "Bieżący miesiąc":

        df_filtered = df[
            (df["Data"].dt.month == today.month)
            &
            (df["Data"].dt.year == today.year)
        ]

    elif okres == "Własny zakres":

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

    # =============================
    # HALA
    # =============================

    hale = sorted(
        df_filtered["Hala"]
        .dropna()
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

    # =============================
    # ZMIANA
    # =============================

    zmiany = sorted(
        df_filtered["Zmiana"]
        .dropna()
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

    # =============================
    # KATEGORIA AWARII
    # =============================

    kategorie = sorted(
        df_filtered["Kategoria awarii"]
        .dropna()
        .unique()
    )

    domyslne = [
        k for k in kategorie
        if "utrzymanie" in k.lower()
    ]

    if len(domyslne) == 0:
        domyslne = kategorie

    wybrane_kategorie = st.sidebar.multiselect(
        "Kategoria awarii",
        options=kategorie,
        default=domyslne
    )

    df_filtered = df_filtered[
        df_filtered["Kategoria awarii"]
        .isin(wybrane_kategorie)
    ]

    # =============================
    # PODKATEGORIA AWARII
    # =============================

    podkategorie = sorted(
        df_filtered["Podkategoria awarii"]
        .dropna()
        .unique()
    )

    wybrane_podkategorie = st.sidebar.multiselect(
        "Podkategoria awarii",
        podkategorie,
        default=podkategorie
    )

    df_filtered = df_filtered[
        df_filtered["Podkategoria awarii"]
        .isin(wybrane_podkategorie)
    ]

    # =============================
    # KPI
    # =============================

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

    oczekiwanie = len(
        df_filtered[
            df_filtered[
                "Kategoria awarii"
            ].str.contains(
                "oczekiwanie",
                case=False,
                na=False
            )
        ]
    )

    przeglady = len(
        df_filtered[
            df_filtered[
                "Podkategoria awarii"
            ].str.contains(
                "przegl",
                case=False,
                na=False
            )
        ]
    )

    awarie = zdarzenia - przeglady

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Zdarzenia", zdarzenia)
    c2.metric("Awarie", awarie)
    c3.metric("Przeglądy", przeglady)
    c4.metric("Oczekiwanie UR", oczekiwanie)
    c5.metric("Maszyny", maszyny)
    c6.metric("MTTR [min]", mttr)

    # =============================
    # TOP MASZYNY
    # =============================

    st.subheader("TOP 10 maszyn")

    top_maszyny = (
        df_filtered["Maszyna-Urządzenie"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_maszyny.columns = [
        "Maszyna",
        "Liczba"
    ]

    st.plotly_chart(
        px.bar(
            top_maszyny,
            x="Maszyna",
            y="Liczba",
            color="Liczba"
        ),
        use_container_width=True
    )

    # =============================
    # TOP PRZYCZYNY
    # =============================

    st.subheader("TOP przyczyn")

    top_przyczyny = (
        df_filtered["Podkategoria awarii"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    top_przyczyny.columns = [
        "Przyczyna",
        "Liczba"
    ]

    st.plotly_chart(
        px.bar(
            top_przyczyny,
            x="Przyczyna",
            y="Liczba",
            color="Liczba"
        ),
        use_container_width=True
    )

    # =============================
    # TREND
    # =============================

    st.subheader("Trend zgłoszeń")

    trend = (
        df_filtered
        .groupby(df_filtered["Data"].dt.date)
        .size()
        .reset_index(name="Liczba")
    )

    st.plotly_chart(
        px.line(
            trend,
            x="Data",
            y="Liczba",
            markers=True
        ),
        use_container_width=True
    )

    # =============================
    # PRACOWNICY
    # =============================

    st.subheader("Ranking pracowników")

    osoby = []

    for wpis in df_filtered[
        "Osoba usuwająca postój, awarię"
    ].dropna():

        osoby_split = (
            str(wpis)
            .replace(",", "\n")
            .split("\n")
        )

        for osoba in osoby_split:

            osoba = osoba.strip()

            if osoba:
                osoby.append(osoba)

    if osoby:

        ranking = (
            pd.Series(osoby)
            .value_counts()
            .head(20)
        )

        st.bar_chart(ranking)

    # =============================
    # DANE
    # =============================

    with st.expander("Pokaż dane"):

        st.dataframe(
            df_filtered,
            use_container_width=True
        )
    
