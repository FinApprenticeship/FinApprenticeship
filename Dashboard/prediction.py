import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from prophet import Prophet
from utils import apply_common_layout_settings

# === Parameter anpassen ===
min_year = 2010  
max_year = 2019  
prediction_years = list(range(2025, 2031)) 

# === Data Loading ===
script_dir = os.path.dirname(__file__)

@st.cache_data
def load_data():
    csv_file_path = os.path.join(script_dir, 'data', 'synthetic_population_with_features.csv.bz2')
    df = pd.read_csv(csv_file_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

def app():
    st.title("📊 Prognose der Vertragslösungsquote")

    df = load_data()

    # --- Sidebar-Filter ---
    st.sidebar.markdown("### 🔍 Auswahlkriterien")
    berufe = sorted(df['sector'].dropna().unique())
    bundeslaender = sorted(df['state'].dropna().unique())
    alter_list = sorted(df['age'].dropna().unique())
    geschlecht_list = sorted(df['gender'].dropna().unique())
    herkunft_list = sorted(df['nationality'].dropna().unique())
    abschluss_list = sorted(df['education'].dropna().unique())

    selected_beruf = st.sidebar.multiselect("Beruf", berufe)
    selected_bundesland = st.sidebar.multiselect("Bundesland", bundeslaender)
    selected_alter = st.sidebar.multiselect("Alter", alter_list)
    selected_geschlecht = st.sidebar.multiselect("Geschlecht", geschlecht_list)
    selected_herkunft = st.sidebar.multiselect("Herkunft", herkunft_list)
    selected_abschluss = st.sidebar.multiselect("Schulabschluss", abschluss_list)

    if not (selected_beruf and selected_bundesland and selected_alter and selected_geschlecht and selected_herkunft and selected_abschluss):
        st.warning("Bitte wähle mindestens eine Option in allen Feldern aus.")
        return

    selected_year = st.selectbox("🗓 Prognosewert für Jahr", prediction_years)

    all_prophet = []

    for beruf in selected_beruf:
        for bundesland in selected_bundesland:
            for alter in selected_alter:
                for geschlecht in selected_geschlecht:
                    for herkunft in selected_herkunft:
                        for abschluss in selected_abschluss:
                            # Filter for this combination
                            combo_mask = (
                                (df['sector'] == beruf) &
                                (df['state'] == bundesland) &
                                (df['age'] == alter) &
                                (df['gender'] == geschlecht) &
                                (df['nationality'] == herkunft) &
                                (df['education'] == abschluss)
                            )
                            df_combo = df[combo_mask]

                            # Dropout-Rate per year (min_year - max_year)
                            dropout_per_year = (
                                df_combo[df_combo["year"].between(min_year, max_year)]
                                .groupby("year")["dropped_out"]
                                .mean()
                                .reset_index()
                            )
                            dropout_per_year["dropped_out"] = dropout_per_year["dropped_out"] * 100  # in %

                            if len(dropout_per_year) >= 2:
                                prophet_df = pd.DataFrame({
                                    "ds": pd.to_datetime(dropout_per_year["year"], format='%Y'),
                                    "y": dropout_per_year["dropped_out"]
                                })
                                m = Prophet(
                                    yearly_seasonality=True,  
                                    weekly_seasonality=False,
                                    daily_seasonality=False
                                )
                                m.fit(prophet_df)
                                future = pd.DataFrame({"ds": pd.to_datetime(prediction_years, format='%Y')})
                                forecast = m.predict(future)
                                trend_pred = forecast["yhat"].values
                                trend_pred = np.clip(trend_pred, 0, 100)  
                            else:
                                trend_pred = [np.nan] * len(prediction_years)
                            
                            prophet_df_out = pd.DataFrame({
                                "Jahr": prediction_years,
                                "Prognose": trend_pred,
                                "Kombination": f"{beruf} | {bundesland} | {geschlecht} | {herkunft} | {abschluss} | {alter}"
                            })
                            all_prophet.append(prophet_df_out)

    if not all_prophet:
        st.error("⚠️ Keine gültigen Vorhersagen gefunden.")
        return

    result = pd.concat(all_prophet)

    # Plot
    fig = px.line(
        result,
        x="Jahr",
        y="Prognose",
        color="Kombination",
        markers=True,
        labels={"Jahr": "Jahr", "Prognose": "Prognose Vertragslösungsquote (%)"},
        title="📈 MPrognose der Vertragslösungsquote"
    )
    fig.update_yaxes(range=[0, 100])
    apply_common_layout_settings(fig)
    fig.update_layout(
        margin_t=50,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            title=None
        ),
        xaxis=dict(dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Anzeige für das gewählte Jahr
    st.markdown(f"## 🌱 Prognose für {selected_year}")
    for label in result["Kombination"].unique():
        value = result[
            (result["Kombination"] == label) &
            (result["Jahr"] == selected_year)
        ]["Prognose"].values
        if value.size > 0:
            st.metric(label=label, value=f"{value[0]:.2f} %")

if __name__ == "__main__":
    app()