    # ====================================
    # TOP 5 TYPÓW MASZYN WG CZASU POSTOJÓW
    # ====================================

    st.subheader(
        "TOP 5 typów maszyn wg czasu postojów"
    )

    top_postoje = (
        df_filtered
        .groupby("Typ")["Czas_min"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(5)
        .reset_index()
    )

    top_postoje["Godziny"] = round(
        top_postoje["Czas_min"] / 60,
        2
    )

    fig_postoje = px.bar(
        top_postoje,
        x="Typ",
        y="Godziny",
        color="Godziny",
        text="Godziny"
    )

    st.plotly_chart(
        fig_postoje,
        use_container_width=True
    )

    st.dataframe(
        top_postoje[
            [
                "Typ",
                "Godziny"
            ]
        ],
        use_container_width=True
    )

    # ====================================
    # TOP 5 NAJDŁUŻSZYCH AWARII
    # ====================================

    st.subheader(
        "TOP 5 najdłuższych awarii"
    )

    top_awarie = (
        df_filtered
        .sort_values(
            by="Czas_min",
            ascending=False
        )
        .head(5)
        .copy()
    )

    top_awarie["Godziny"] = round(
        top_awarie["Czas_min"] / 60,
        2
    )

    st.dataframe(
        top_awarie[
            [
                "Data",
                "Typ",
                "Maszyna-Urządzenie",
                "Podkategoria awarii",
                "Godziny"
            ]
        ],
        use_container_width=True
    )

    # ====================================
    # TOP PRZYCZYN
    # ====================================

    st.subheader(
        "TOP 10 przyczyn"
    )

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

    fig2 = px.bar(
        top_przyczyny,
        x="Przyczyna",
        y="Liczba",
        color="Liczba",
        text="Liczba"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ====================================
    # TREND
    # ====================================

    st.subheader(
        "Trend zgłoszeń"
    )

    trend = (
        df_filtered
        .groupby(
            df_filtered["Data"].dt.date
        )
        .size()
        .reset_index(
            name="Liczba"
        )
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

    # ====================================
    # RAPORT MENEDŻERSKI
    # ====================================

    if len(df_filtered):

        top_typ = (
            top_postoje.iloc[0]["Typ"]
        )

        top_czas = (
            top_postoje.iloc[0]["Godziny"]
        )

        st.info(
            f"""
W analizowanym okresie odnotowano {zdarzenia} zdarzeń.

Łączny czas postojów wyniósł {postoj_h} godzin.

Średni czas zdarzenia (MTTR) wyniósł {mttr} minut.

Największy udział w postojach miał typ maszyny:

{top_typ}

Łączny czas postojów dla tego typu wyniósł:

{top_czas} h.

Zaleca się przeprowadzenie analizy przyczyn źródłowych
oraz zwiększenie działań prewencyjnych dla maszyn
tego typu.
"""
        )

    # ====================================
    # DANE
    # ====================================

    with st.expander(
        "Pokaż dane źródłowe"
    ):

        st.dataframe(
            df_filtered,
            use_container_width=True
        )
