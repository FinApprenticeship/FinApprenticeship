import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("../data/dazubi_grouped_berufe.csv")

    abschluss_mapping = {
        "Höchster allgemeinbildender Schulabschluss Studienberechtigung": "Studienberechtigung",
        "Höchster allgemeinbildender Schulabschluss mit Hauptschulabschluss": "Hauptschulabschluss",
        "Höchster allgemeinbildender Schulabschluss Realschulabschluss": "Realschulabschluss",
        "Höchster allgemeinbildender Schulabschluss ohne Hauptschulabschluss": "ohne Abschluss",
        "Höchster allgemeinbildender Schulabschluss nicht zuzuordnen": "nicht zuzuordnen"
    }

    df = df.rename(columns=abschluss_mapping)
    df = df[df["Jahr"] != 2020]
    return df, abschluss_mapping

def forecast_for_combination(df, beruf, region, alter, abschluss_colname, herkunft):
    df_filtered = df[
        (df["Beruf_clean"] == beruf) &
        (df["Region"] == region) &
        (df[alter].notna()) &
        (df[abschluss_colname].notna()) &
        (df[herkunft].notna())
    ].copy()

    # Prüfe, ob genug Azubis in dieser Abschlussgruppe vorhanden sind
    if df_filtered[abschluss_colname].sum() < 20:
        return None, None

    df_filtered["ds"] = pd.to_datetime(df_filtered["Jahr"], format="%Y")
    denominator = df_filtered[abschluss_colname].replace(0, pd.NA)

    df_filtered["y"] = (
        df_filtered["Vorzeitige Vertragslösungen Insgesamt"] / denominator * 100
    )

    df_filtered = df_filtered.replace([float("inf"), -float("inf")], pd.NA).dropna(subset=["y"])
    df_filtered = df_filtered[df_filtered["y"] <= 100]

    df_forecast = df_filtered[["ds", "y"]]
    if df_forecast.shape[0] < 2:
        return None, None

    m = Prophet()
    m.fit(df_forecast)
    future = m.make_future_dataframe(periods=6, freq="Y")
    forecast = m.predict(future)
    forecast["yhat"] = forecast["yhat"].clip(upper=100)
    return forecast[forecast["ds"].dt.year.between(2025, 2030)], m

def app():
    st.title("📊 Vorhersage der Vertragslösungsquote (2025–2030)")

    df, abschluss_mapping = load_data()

    st.sidebar.markdown("### 🔍 Auswahlkriterien")
    selected_jobs = st.sidebar.multiselect("Berufe", sorted(df["Beruf_clean"].dropna().unique()))
    selected_states = st.sidebar.multiselect("Bundesländer", ["Alle"] + sorted(df["Region"].dropna().unique()))
    selected_ages = st.sidebar.multiselect("Altersgruppen", [col for col in df.columns if col.startswith("im Alter von:")])
    selected_origins = st.sidebar.multiselect("Herkunft / Geschlecht", [
        "Deutsche Männer", "Deutsche Frauen", "Ausländer/-innen Männer", "Ausländer/-innen Frauen"
    ])
    selected_graduations = st.sidebar.multiselect("Schulabschluss", list(abschluss_mapping.values()))

    if "Alle" in selected_states:
        selected_states = sorted(df["Region"].dropna().unique())

    selected_year = st.selectbox("🗓 Jahr für Einzelprognosewert", list(range(2025, 2031)))

    if not (selected_jobs and selected_states and selected_ages and selected_origins and selected_graduations):
        st.warning("Bitte wähle mindestens eine Option in allen Feldern aus.")
        return

    forecasts = []
    for beruf in selected_jobs:
        for region in selected_states:
            for alter in selected_ages:
                for abschluss in selected_graduations:
                    abschluss_colname = abschluss
                    for herkunft in selected_origins:
                        fc, model = forecast_for_combination(df, beruf, region, alter, abschluss_colname, herkunft)
                        if fc is not None:
                            label = f"{beruf} | {region} | {herkunft} | {abschluss} | {alter}"
                            fc["Kombination"] = label
                            forecasts.append(fc)

    if not forecasts:
        st.error("⚠️ Keine gültigen Daten mit ausreichend Azubis (≥ 20) in der Abschlussgruppe gefunden.")
        return

    result = pd.concat(forecasts)

    fig = px.line(
        result,
        x="ds",
        y="yhat",
        color="Kombination",
        labels={"ds": "Jahr", "yhat": "Vertragslösungen in %"},
        title="📈 Prognose der Vertragslösungsquote",
        markers=True
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            title=None
        ),
        xaxis=dict(dtick="M12", tickformat="%Y")
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"## 🌱 Prognosewerte für {selected_year}")
    year_values = result[result["ds"].dt.year == selected_year]

    for label in year_values["Kombination"].unique():
        value = year_values[year_values["Kombination"] == label]["yhat"].values[0]
        st.metric(label=label, value=f"{value:.2f} %")