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

    # -------------------------
    # ODCZYT EXCELA
    # -------------------------

    df = pd.read_excel(
        uploaded_file,
        header=2
    )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    df = df.dropna(
        subset=["Data"],
        errors="ignore"
    )

    # -------------------------
    # DATA
    # -------------------------

    df["Data"] = pd.to_datetime(
        df["Data"],
        errors="coerce"
    )

    # -------------------------
    # CZAS
    # -------------------------

    def convert_time_to_minutes(value):

        try:

            td = pd.to_timedelta(
                str(value)
            )

            return td.total_seconds() / 60

        except:

            return 0

    df["Czas_min"] = df["Czas"].apply(
        convert_time_to_minutes
    )

    # -------------------------
    # SIDEBAR
    # -------------------------

    st.sidebar.header("Filtry")

    zakres = st.sidebar.radio(
        "Okres",
        [
            "Dzisiaj",
            "Bieżący tydzień",
            "Bieżący miesiąc",
            "Własny zakres"
        ]
    )

    today = pd.Timestamp.today().normalize()

    if zakres == "Dzisiaj":

        data_od = today
        data_do = today

    elif zakres == "Bieżący tydzień":

        data_od = today - pd.Timedelta(
            days=today.weekday()
        )

        data_do = data_od + pd.Timedelta(days=6)

    elif zakres == "Bieżący miesiąc":

        data_od = today.replace(day=1)
        data_do = today

    else:

        data_od = pd.Timestamp(
            st.sidebar.date_input(
                "Data od"
            )
        )

        data_do = pd.Timestamp(
            st.sidebar.date_input(
                "Data do"
            )
        )

    df_filtered = df.copy()

    df_filtered = df_filtered[
        (df_filtered["Data"] >= data_od)
        &
        (df_filtered["Data"] <= data_do)
    ]

    # -------------------------
    # HALA
    # -------------------------

    if "Hala" in df.columns:

        hale = sorted(
            df["Hala"]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_hale = st.sidebar.multiselect(
            "Hala",
            hale,
            default=hale
        )

        df_filtered = df_filtered[
            df_filtered["Hala"]
            .astype(str)
            .isin(selected_hale)
        ]

    # -------------------------
    # ZMIANA
    # -------------------------

    if "Zmiana" in df.columns:

        zmiany = sorted(
            df["Zmiana"]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_zmiany = st.sidebar.multiselect(
            "Zmiana",
            zmiany,
            default=zmiany
        )

        df_filtered = df_filtered[
            df_filtered["Zmiana"]
            .astype(str)
            .isin(selected_zmiany)
        ]

    # -------------------------
    # KPI
    # -------------------------

    liczba_zdarzen = len(df_filtered)

    laczny_czas_min = (
        df_filtered["Czas_min"].sum()
    )

    laczny_czas_h = round(
        laczny_czas_min / 60,
        1
    )

    mttr = round(
        df_filtered["Czas_min"].mean(),
        1
    ) if liczba_zdarzen > 0 else 0

    liczba_maszyn = (
        df_filtered["Maszyna-Urządzenie"]
        .nunique()
    )

    awarie = len(
        df_filtered[
            ~df_filtered[
                "Podkategoria awarii"
            ]
            .astype(str)
            .str.contains(
                "przegląd|zadanie",
                case=False,
                na=False
            )
        ]
    )

    przeglady = len(
        df_filtered[
            df_filtered[
                "Podkategoria awarii"
            ]
            .astype(str)
            .str.contains(
                "przegląd",
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

    # -------------------------
    # RAPORT
    # -------------------------

    st.divider()

    top_machine = "-"

    if len(df_filtered):

        top_machine = (
            df_filtered[
                "Maszyna-Urządzenie"
            ]
            .value_counts()
            .index[0]
        )

    top_reason = "-"

    if len(df_filtered):

        top_reason = (
            df_filtered[
                "Podkategoria awarii"
            ]
            .astype(str)
            .value_counts()
            .index[0]
        )

    st.subheader(
        "Komentarz menedżerski"
    )

    st.info(
        f"""
W analizowanym okresie odnotowano {liczba_zdarzen} zdarzeń.

Łączny czas działań wyniósł {laczny_czas_h} godzin.

Średni czas interwencji MTTR wyniósł {mttr} minut.

Zarejestrowano {awarie} awarii,
{przeglady} przeglądów oraz
{zadania} zadań planowanych.

Najczęściej obsługiwaną maszyną była:
{top_machine}.

Najczęściej występująca podkategoria:
{top_reason}.
"""
    )

    # -------------------------
    # TABS
    # -------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "Dashboard",
            "Pracownicy",
            "Dane"
        ]
    )

    # -------------------------
    # DASHBOARD
    # -------------------------

    with tab1:

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
            y="Liczba"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader(
            "TOP 10 przyczyn"
        )

        top_przyczyny = (
            df_filtered[
                "Podkategoria awarii"
            ]
            .astype(str)
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

        trend = (
            df_filtered
            .groupby(
                df_filtered["Data"].dt.date
            )
            .size()
            .reset_index(name="Liczba")
        )

        fig3 = px.line(
            trend,
            x="Data",
            y="Liczba",
            markers=True,
            title="Trend zgłoszeń"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    # -------------------------
    # PRACOWNICY
    # -------------------------

    with tab2:

        wszystkie_osoby = []

        for row in df_filtered[
            "Osoba usuwająca postój, awarię"
        ].dropna():

            osoby = (
                str(row)
                .replace(",", "\n")
                .split("\n")
            )

            for osoba in osoby:

                osoba = osoba.strip()

                if osoba:
                    wszystkie_osoby.append(
                        osoba
                    )

        if wszystkie_osoby:

            ranking = (
                pd.Series(
                    wszystkie_osoby
                )
                .value_counts()
                .head(15)
            )

            st.bar_chart(ranking)

            st.dataframe(
                ranking.rename(
                    "Liczba interwencji"
                )
            )

    # -------------------------
    # DANE
    # -------------------------

    with tab3:

        st.dataframe(
            df_filtered,
            use_container_width=True
        )
   
