import streamlit as st
import pandas as pd
import xgboost as xgb
import plotly.express as px
import numpy as np
import os

script_dir = os.path.dirname(__file__)

@st.cache_data
def load_data():
    csv_file_path = os.path.join(script_dir, '..', 'data', 'synthetic_population_with_features.csv')
    df = pd.read_csv(csv_file_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

@st.cache_resource
def load_xgb_model():
    model = xgb.Booster()
    model_file_path = os.path.join(script_dir, '..', 'models', 'MLflow', 'model.xgb')
    model.load_model(model_file_path)
    return model

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
    st.title("📊 Prognose der Vertragslösungsquote")

    df = load_data()
    model = load_xgb_model()

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

    prediction_years = list(range(2025, 2031))
    selected_year = st.selectbox("🗓 Prognosewert für Jahr", prediction_years)

    model_features = [
        "age", "education", "year", "state", "gender", "sector", "nationality"
    ]
    numerics = [col for col in df.columns if col not in model_features + ['dropped_out']]
    model_features += numerics

    forecasts = []
    for beruf in selected_beruf:
        for bundesland in selected_bundesland:
            for alter in selected_alter:
                for geschlecht in selected_geschlecht:
                    for herkunft in selected_herkunft:
                        for abschluss in selected_abschluss:
                            template = get_template_row(df, beruf, bundesland, alter, geschlecht, herkunft, abschluss)
                            rows = []
                            for jahr in prediction_years:
                                row = template.copy()
                                row["year"] = jahr
                                row_df = pd.DataFrame([row])[model_features]
                                cat_cols = ["age", "education", "state", "gender", "sector", "nationality"]
                                row_df = encode_input(row_df, df, cat_cols)
                                for nc in numerics:
                                    row_df[nc] = pd.to_numeric(row_df[nc], errors='coerce')
                                dmatrix = xgb.DMatrix(row_df)
                                pred = model.predict(dmatrix)[0]
                                
                                if pred < 1:  
                                    pred = pred * 100
                                pred = np.clip(pred, 0, 100)

                                rows.append({
                                    "Jahr": jahr,
                                    "Prognose": pred,
                                    "Kombination": f"{beruf} | {bundesland} | {geschlecht} | {herkunft} | {abschluss} | {alter}"
                                })
                            forecasts.append(pd.DataFrame(rows))

    if not forecasts:
        st.error("⚠️ Keine gültigen Vorhersagen gefunden.")
        return

    result = pd.concat(forecasts)

    fig = px.line(
        result,
        x="Jahr",
        y="Prognose",
        color="Kombination",
        markers=True,
        labels={"Jahr": "Jahr", "Prognose": "Vorhersage Vertragslösungsquote (%)"},
        title="📈 Prognose der Vertragslösungsquote"
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
        xaxis=dict(dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"## 🌱 Prognosewerte für {selected_year}")
    year_values = result[result["Jahr"] == selected_year]
    for label in year_values["Kombination"].unique():
        value = year_values[year_values["Kombination"] == label]["Prognose"].values[0]
        st.metric(label=label, value=f"{value:.2f} %")

if __name__ == "__main__":
    app()