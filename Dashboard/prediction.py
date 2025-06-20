import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import bz2
from prophet import Prophet
import xgboost as xgb
from utils import apply_common_layout_settings

# === Parameters for historical and prediction years ===
min_year = 2010  # Start year for historical data used in Prophet
max_year = 2019  # End year for historical data because of the COVID year (adjust as needed)
prediction_years = list(range(2025, 2031))  # Forecast years for the plot and metrics

# === Data Loading Functions ===

script_dir = os.path.dirname(__file__)

@st.cache_data
def load_data():
    csv_file_path = os.path.join(script_dir, 'data', 'synthetic_population_with_features.csv.bz2')
    df = pd.read_csv(csv_file_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

@st.cache_resource
def load_xgb_model():
    model = xgb.Booster()
    model_file_path = os.path.join(script_dir, 'data', 'model.xgb.bz2')
    with bz2.open(model_file_path, 'rb') as f:
        model.load_model(bytearray(f.read()))
    return model

# Encode categorical columns in a row (as used in training). Categories are assigned integer indices.

def encode_input(row_df, df, cat_cols):
    for col in cat_cols:
        cats = list(df[col].dropna().unique())
        row_df[col] = row_df[col].apply(lambda x: cats.index(x) if x in cats else -1)
    return row_df

def get_template_row(df, beruf, bundesland, alter, geschlecht, herkunft, abschluss):
    match = df[
        (df['sector'] == beruf) &
        (df['state'] == bundesland) &
        (df['age'] == alter) &
        (df['gender'] == geschlecht) &
        (df['nationality'] == herkunft) &
        (df['education'] == abschluss)
    ]
    if not match.empty:
        return match.sort_values("year").iloc[-1]
    else:
        return df.iloc[0]

def app():
    st.title("Prognose der Vertragslösungsquote")

    # === Load data and ML model ===
    df = load_data()
    model = load_xgb_model()

    # --- Sidebar filters for user selection ---
    st.sidebar.markdown("### 🔍 Auswahlkriterien")
    berufe = sorted(df['sector'].dropna().unique())
    bundeslaender = sorted(df['state'].dropna().unique())
    alter_list = sorted(df['age'].dropna().unique())
    geschlecht_list = sorted(df['gender'].dropna().unique())
    herkunft_list = sorted(df['nationality'].dropna().unique())
    abschluss_list = sorted(df['education'].dropna().unique())

    # User selections for all relevant fields
    selected_beruf = st.sidebar.multiselect("Beruf", berufe)
    selected_bundesland = st.sidebar.multiselect("Bundesland", bundeslaender)
    selected_alter = st.sidebar.multiselect("Alter", alter_list)
    selected_geschlecht = st.sidebar.multiselect("Geschlecht", geschlecht_list)
    selected_herkunft = st.sidebar.multiselect("Herkunft", herkunft_list)
    selected_abschluss = st.sidebar.multiselect("Schulabschluss", abschluss_list)

    # Prevent empty input for any filter
    if not (selected_beruf and selected_bundesland and selected_alter and selected_geschlecht and selected_herkunft and selected_abschluss):
        st.warning("Bitte wähle mindestens eine Option in allen Feldern aus.")
        return

    # Select the year for metric output
    selected_year = st.selectbox("Prognosewert für Jahr", prediction_years)

    # Prepare feature list for ML input (all except 'dropped_out' and 'Unnamed: 0')
    model_features = [col for col in df.columns if col not in ['dropped_out', 'Unnamed: 0']]

    # Collect all forecast results for the selected combinations
    all_hybrid = []

    for beruf in selected_beruf:
        for bundesland in selected_bundesland:
            for alter in selected_alter:
                for geschlecht in selected_geschlecht:
                    for herkunft in selected_herkunft:
                        for abschluss in selected_abschluss:
                            # filter for this combination
                            combo_mask = (
                                (df['sector'] == beruf) &
                                (df['state'] == bundesland) &
                                (df['age'] == alter) &
                                (df['gender'] == geschlecht) &
                                (df['nationality'] == herkunft) &
                                (df['education'] == abschluss)
                            )
                            df_combo = df[combo_mask]

                            # dropout rate per year (min_year - max_year)
                            dropout_per_year = (
                                df_combo[df_combo["year"].between(min_year, max_year)]
                                .groupby("year")["dropped_out"]
                                .mean()
                                .reset_index()
                            )
                            dropout_per_year["dropped_out"] = dropout_per_year["dropped_out"] * 100  # in %

                            # --- Prophet Forecast ---
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
                                prophet_pred = forecast["yhat"].values
                                prophet_pred = np.clip(prophet_pred, 0, 100)
                            else:
                                prophet_pred = [np.nan] * len(prediction_years)

                            # --- XGBoost Model prediction for predictionyear ---
                            template = get_template_row(df, beruf, bundesland, alter, geschlecht, herkunft, abschluss)
                            model_preds = []
                            for jahr in prediction_years:
                                row = template.copy()
                                row["year"] = jahr
                                row_df = pd.DataFrame([row])[model_features]
                                cat_cols = ["age", "education", "state", "gender", "sector", "nationality"]
                                row_df = encode_input(row_df, df, cat_cols)
                                frow_df = row_df.apply(pd.to_numeric, errors='ignore')
                                dmatrix = xgb.DMatrix(row_df)
                                pred = model.predict(dmatrix)[0]
                                if pred < 1:  
                                    pred = pred * 100
                                pred = np.clip(pred, 0, 100)
                                model_preds.append(pred)

                            # --- Hybrid: Mean of Prophet & Model (if both values are available) ---
                            hybrid_pred = []
                            for p, m in zip(prophet_pred, model_preds):
                                if np.isnan(p):
                                    hybrid_pred.append(m)
                                else:
                                    # Weighting Prophet:Model
                                    hybrid_pred.append(0.5 * p + 0.5 * m)

                            # output
                            df_out = pd.DataFrame({
                                "Jahr": prediction_years,
                                "Prognose": hybrid_pred,
                                "Kombination": f"{beruf} | {bundesland} | {geschlecht} | {herkunft} | {abschluss} | {alter}"
                            })
                            all_hybrid.append(df_out)

    if not all_hybrid:
        st.error("⚠️ Keine gültigen Vorhersagen gefunden.")
        return

    result = pd.concat(all_hybrid)

    # ==== Dynamischen y-Achsenbereich bestimmen ====
    y_min = max(0, result["Prognose"].min() - 2)
    y_max = min(100, result["Prognose"].max() + 2)

    # Plot
    fig = px.line(
        result,
        x="Jahr",
        y="Prognose",
        color="Kombination",
        markers=True,
        labels={"Jahr": "Jahr", "Prognose": "Prognose Vertragslösungsquote (%)"},
        title="Prognose (Prophet + Modell) der Vertragslösungsquote (2025–2030)"
    )
    fig.update_yaxes(range=[y_min, y_max])
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

    st.markdown(f"## Prognose für {selected_year}")
    for label in result["Kombination"].unique():
        value = result[
            (result["Kombination"] == label) &
            (result["Jahr"] == selected_year)
        ]["Prognose"].values
        if value.size > 0:
            st.metric(label=label, value=f"{value[0]:.2f} %")

if __name__ == "__main__":
    app()
