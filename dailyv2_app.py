import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(
    page_title="UR Insight",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 UR Insight")
st.subheader("Analiza rejestru awarii Utrzymania Ruchu")

uploaded_file = st.file_uploader(
    "Wybierz plik XLSX",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    df.columns = [str(c).strip() for c in df.columns]

    # -----------------
    # DATY
    # -----------------

    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(
            df["Data"],
            errors="coerce"
        )

    # -----------------
    # CZAS
    # -----------------

    if "Czas" in df.columns:

        def parse_time(x):
            try:
                parts = str(x).split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except:
                return 0

        df["Czas_min"] = df["Czas"].astype(str).apply(parse_time)

    else:
        df["Czas_min"] = 0

    # ===========================
    # FILTRY
    # ===========================

    st.sidebar.header("Filtry")

    okres = st.sidebar.selectbox(
        "Zakres danych",
        [
            "Dzisiaj",
            "Bieżący tydzień",
            "Bieżący miesiąc",
            "Własny zakres"
        ]
    )

    today = pd.Timestamp.today().normalize()

    if okres == "Dzisiaj":

        start_date = today
        end_date = today

    elif okres == "Bieżący tydzień":

        start_date = today - pd.Timedelta(
            days=today.weekday()
        )

        end_date = start_date + pd.Timedelta(days=6)

    elif okres == "Bieżący miesiąc":

        start_date = today.replace(day=1)

        if today.month == 12:
            end_date = pd.Timestamp(
                year=today.year + 1,
                month=1,
                day=1
            ) - pd.Timedelta(days=1)
        else:
            end_date = pd.Timestamp(
                year=today.year,
                month=today.month + 1,
                day=1
            ) - pd.Timedelta(days=1)

    else:

        start_date = pd.Timestamp(
            st.sidebar.date_input(
                "Data od",
                value=today.date()
            )
        )

        end_date = pd.Timestamp(
            st.sidebar.date_input(
                "Data do",
                value=today.date()
            )
        )

    df_filtered = df.copy()

    if "Data" in df.columns:

        df_filtered = df_filtered[
            (df_filtered["Data"] >= start_date)
            &
            (df_filtered["Data"] <= end_date)
        ]

    # Hala

    if "Hala" in df.columns:

        hale = sorted(
            df["Hala"].dropna().astype(str).unique()
        )

        selected_hale = st.sidebar.multiselect(
            "Hala",
            hale,
            default=hale
        )

        df_filtered = df_filtered[
            df_filtered["Hala"].astype(str)
            .isin(selected_hale)
        ]

    # Zmiana

    if "Zmiana" in df.columns:

        zmiany = sorted(
            df["Zmiana"].dropna().astype(str).unique()
        )

        selected_zmiany = st.sidebar.multiselect(
            "Zmiana",
            zmiany,
            default=zmiany
        )

        df_filtered = df_filtered[
            df_filtered["Zmiana"].astype(str)
            .isin(selected_zmiany)
        ]

    # ===========================
    # KPI
    # ===========================

    liczba_zdarzen = len(df_filtered)

    czas_min = df_filtered["Czas_min"].sum()

    czas_h = round(czas_min / 60, 2)

    mttr = round(
        df_filtered["Czas_min"].mean(),
        1
    ) if liczba_zdarzen > 0 else 0

    liczba_maszyn = 0

    if "Maszyna-Urządzenie" in df_filtered.columns:
        liczba_maszyn = (
            df_filtered["Maszyna-Urządzenie"]
            .nunique()
        )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Interwencje",
        liczba_zdarzen
    )

    col2.metric(
        "Czas awarii [h]",
        czas_h
    )

    col3.metric(
        "MTTR [min]",
        mttr
    )

    col4.metric(
        "Maszyny",
        liczba_maszyn
    )

    # ===========================
    # RAPORT AI
    # ===========================

    st.divider()

    st.subheader("Komentarz menedżerski")

    top_machine = "-"
    top_category = "-"
    top_employee = "-"

    if (
        "Maszyna-Urządzenie"
        in df_filtered.columns
    ) and len(df_filtered):

        top_machine = (
            df_filtered["Maszyna-Urządzenie"]
            .value_counts()
            .index[0]
        )

    if (
        "Podkategoria awarii"
        in df_filtered.columns
    ) and len(df_filtered):

        top_category = (
            df_filtered["Podkategoria awarii"]
            .astype(str)
            .value_counts()
            .index[0]
        )

    if (
        "Osoba usuwająca postój, awarię"
        in df_filtered.columns
    ) and len(df_filtered):

        top_employee = (
            df_filtered[
                "Osoba usuwająca postój, awarię"
            ]
            .astype(str)
            .value_counts()
            .index[0]
        )

    st.info(
        f"""
W analizowanym okresie wykonano {liczba_zdarzen} interwencji.

Łączny czas działań wyniósł {czas_h} godzin.

Średni czas interwencji (MTTR) wyniósł {mttr} minut.

Najwięcej zgłoszeń dotyczyło maszyny:
{top_machine}.

Dominująca podkategoria:
{top_category}.

Największe zaangażowanie wykazali:
{top_employee}.

Zaleca się przeanalizowanie przyczyn najczęściej
występujących zdarzeń oraz wdrożenie działań
prewencyjnych dla najbardziej awaryjnych maszyn.
"""
    )

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "Dashboard",
            "Raport tygodniowy",
            "Dane"
        ]
    )

    # ===========================
    # DASHBOARD
    # ===========================

    with tab1:

        if (
            "Maszyna-Urządzenie"
            in df_filtered.columns
        ):

            top10 = (
                df_filtered[
                    "Maszyna-Urządzenie"
                ]
                .value_counts()
                .head(10)
                .reset_index()
            )

            top10.columns = [
                "Maszyna",
                "Liczba"
            ]

            fig = px.bar(
                top10,
                x="Maszyna",
                y="Liczba",
                title="TOP 10 maszyn"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        if (
            "Podkategoria awarii"
            in df_filtered.columns
        ):

            top_cat = (
                df_filtered[
                    "Podkategoria awarii"
                ]
                .astype(str)
                .value_counts()
                .head(10)
                .reset_index()
            )

            top_cat.columns = [
                "Przyczyna",
                "Liczba"
            ]

            fig2 = px.bar(
                top_cat,
                x="Przyczyna",
                y="Liczba",
                title="TOP 10 przyczyn"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # ===========================
    # TREND
    # ===========================

    with tab2:

        if "Data" in df_filtered.columns:

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

    # ===========================
    # DANE
    # ===========================

    with tab3:

        st.dataframe(
            df_filtered,
            use_container_width=True
        )
