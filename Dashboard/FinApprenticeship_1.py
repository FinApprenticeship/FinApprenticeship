import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet

# OPTIONAL: XGBoost
import xgboost as xgb

# ---------- SETTINGS ----------
CSV_PATH = "synthetic_population_with_dropout_rate.csv"
IMAGE_PATH = "FinApprenticeship.png"
XGB_MODEL_PATH = "../models/model.xgb"   

st.set_page_config(layout="wide", page_title="FinApprenticeship Dropout Risk")

# --------- Custom CSS ----------
st.markdown("""
    <style>
    body { background-color: #153857; }
    .css-1d391kg { background-color: #22232c !important; }
    .css-1v0mbdj { background-color: #22232c !important; }
    .risk-number { font-size: 56px; color: #2de2e6; font-weight: bold; margin-bottom: 10px;}
    .ampel-green { background: #166b84; color: #1ee682; border-radius: 16px; padding: 8px; text-align: center; margin: 2px;}
    .ampel-red   { background: #7e1b1b; color: #ff6a6a; border-radius: 16px; padding: 8px; text-align: center; margin: 2px;}
    .css-1aumxhk { color: #2de2e6 !important; }
    .block { background: #1d4263; border-radius: 18px; padding: 28px 20px; margin-bottom: 16px;}
    .stButton button { background-color: #153857 !important; color: #2de2e6 !important; border-radius: 16px; }
    </style>
""", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
df = pd.read_csv(CSV_PATH)
df["year"] = df["year"].astype(int)

# ---- XGBoost model laden ----
xgb_model = None
try:
    xgb_model = xgb.Booster()
    xgb_model.load_model(XGB_MODEL_PATH)
except Exception as e:
    st.warning(f"XGBoost model could not be loaded: {e}")

# ---- FEATURES used by our MODEL ----
feature_columns = [
    'age', 'education', 'year', 'state', 'gender', 'sector', 'nationality',
    'Emp_Age_25_34_Share', 'Emp_Age_35_49_Share', 'Emp_Age_50_Plus_Share', 'Emp_Age_Under_25_Share',
    'Emp_Bachelor_Share', 'Emp_Diplom_Magister_StateExam_Share', 'Emp_Foreign_Share',
    'Emp_Index', 'Emp_Master_Tech_Share', 'Emp_No_Vocational_Edu_Share', 'Emp_PartTime_Share',
    'Emp_Promotion_Share', 'Emp_Recognized_Vocational_Edu_Share', 'Emp_Sector_Agriculture_Share',
    'Emp_Sector_Construction_Share', 'Emp_Sector_Manufacturing_Machinery_Share',
    'Emp_Sector_Manufacturing_Other_Share', 'Emp_Sector_Manufacturing_Share',
    'Emp_Sector_Services_Edu_Culture_Share', 'Emp_Sector_Services_Finance_Insurance_Share',
    'Emp_Sector_Services_Health_Social_Share', 'Emp_Sector_Services_Other_Share',
    'Emp_Sector_Services_Public_Admin_Share', 'Emp_Sector_Services_Share',
    'Emp_Sector_Services_Trade_Share', 'Emp_Sector_Services_Transport_Com_Share',
    'Emp_Total_Count', 'Emp_Vocational_Edu_Unknown_Share', 'Emp_Women_Share',
    'Unemp_Age_25_34_Share', 'Unemp_Age_35_49_Share', 'Unemp_Age_50_Plus_Share', 'Unemp_Age_Under_25_Share',
    'Unemp_Bachelor_Share', 'Unemp_Diplom_Magister_Master_StateExam_Share', 'Unemp_Edu_Unknown_Share',
    'Unemp_Foreign_Share', 'Unemp_Index_2013_100', 'Unemp_LongTerm_Share', 'Unemp_No_Vocational_Edu_Share',
    'Unemp_Promotion_Share', 'Unemp_Rate_Men', 'Unemp_Rate_Total', 'Unemp_Rate_Women',
    'Unemp_Total_Count', 'Unemp_Vocational_Training_Share', 'Unemp_Women_Share',
    'nominal_wage_index', 'nominal_wage_growth_rate'
]

# --------------- Sidebar / User Input ---------------
with st.sidebar:
    st.image(IMAGE_PATH, use_container_width=True)
    st.markdown("## Your Profile")
    state = st.selectbox("Federal State", sorted(df["state"].unique()))
    sector = st.selectbox("Occupation Sector", sorted(df["sector"].unique()))
    education = st.selectbox("School Degree", sorted(df["education"].unique()))
    age = st.selectbox("Age", sorted(df["age"].unique(), key=lambda x: int(str(x).split()[0]) if str(x).split()[0].isdigit() else 100))

    # Years: 2024 as forecast, 2025–2030 as forecast as well
    all_years = sorted(df["year"].unique())
    display_years = [y for y in all_years if y < 2024] + list(range(2024, 2031))
    year = st.selectbox("Year", display_years)
    show_features = st.checkbox("Show all features for this selection")

# ------------------ Main Panel -----------------
col1, col2 = st.columns([1, 2])
with col2:
    st.image(IMAGE_PATH, use_container_width=True)
    st.markdown("<h1 style='color:#2de2e6;'>FinApprenticeship Dropout Risk</h1>", unsafe_allow_html=True)

# --------- Zeitachsen-Logik für Prophet ---------
past_years = [y for y in all_years if y < 2024]
forecast_years = list(range(2024, 2031))  # Prophet for 2024+ (inkl. 2024)

dropout = None

# -------------- Dropout Risk Anzeige --------------
if int(year) < 2024:
    # Historische Daten direkt anzeigen
    mask = (
        (df["state"] == state)
        & (df["sector"] == sector)
        & (df["education"] == education)
        & (df["age"] == age)
        & (df["year"] == int(year))
    )
    this_row = df[mask]
    if not this_row.empty:
        dropout = this_row["dropout_rate"].values[0]
        st.markdown(f"<div class='risk-number'>{dropout*100:.1f}%</div><div style='font-size:20px;'>Dropout Risk in {year}</div>", unsafe_allow_html=True)
    else:
        st.warning("No data available for your selection.")
        dropout = np.nan

elif int(year) in forecast_years:
    # Prophet Forecast auch für 2024!
    ts_mask = (
        (df["state"] == state)
        & (df["sector"] == sector)
        & (df["education"] == education)
        & (df["age"] == age)
        & (df["year"].isin(past_years))
    )
    ts = df[ts_mask][["year", "dropout_rate"]].sort_values("year")
    if len(ts) >= 2:
        ts_grouped = ts.groupby("year").mean().reset_index()
        ts_grouped.rename(columns={"year": "ds", "dropout_rate": "y"}, inplace=True)
        try:
            ts_grouped['ds'] = pd.to_datetime(ts_grouped['ds'], format='%Y')
            m = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=False)
            m.fit(ts_grouped)
            last_year = ts_grouped['ds'].dt.year.max()
            periods = int(year) - last_year
            if periods >= 0:
                future = m.make_future_dataframe(periods=periods, freq='Y')
                forecast = m.predict(future)
                forecast['year'] = forecast['ds'].dt.year
                pred_row = forecast[forecast['year'] == int(year)]
                if not pred_row.empty:
                    yhat = pred_row.iloc[0]['yhat']
                    dropout = yhat
                    st.markdown(f"<div class='risk-number'>{dropout*100:.1f}%</div><div style='font-size:20px;'>Predicted Dropout Risk for {year} (Prophet)</div>", unsafe_allow_html=True)
                    if dropout > 0.4:
                        st.info("⚠️ The predicted dropout risk is **high**. Tips: Consider extra tutoring, seek career counseling, and check if your apprenticeship matches your interests.")
                else:
                    st.warning("No prediction available for this year (model failed to extrapolate).")
                    dropout = np.nan
            else:
                st.warning("Year must be >= your last data year for prediction.")
                dropout = np.nan
        except Exception as e:
            st.error(f"Prediction failed due to: {e}")
            dropout = np.nan
    else:
        st.warning("Not enough data for a prediction.")
        dropout = np.nan

# ------- (OPTIONAL) XGBoost Model Prediction -----------
# ------- (OPTIONAL) XGBoost Model Prediction -----------
cat_features = ['age', 'education', 'state', 'gender', 'sector', 'nationality']

if xgb_model is not None:
    xgb_row = df[
        (df["state"] == state)
        & (df["sector"] == sector)
        & (df["education"] == education)
        & (df["age"] == age)
        & (df["year"] == int(year))
    ]
    if not xgb_row.empty:
        try:
            # Wandelt alle kategorischen Features in echte Pandas-Kategorien um
            for col in cat_features:
                if col in xgb_row:
                    xgb_row[col] = xgb_row[col].astype("category")
            X_input = xgb_row[feature_columns]
            dmatrix = xgb.DMatrix(X_input, enable_categorical=True)
            dropout_mlflow = xgb_model.predict(dmatrix)[0]
            st.markdown(f"<div class='risk-number'>{dropout_mlflow*100:.1f}%</div><div style='font-size:20px;'>Predicted Dropout Risk (XGBoost Model) for {year}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"XGBoost prediction not possible: {e}")
    else:
        st.info("No row with all features for this selection. XGBoost Prediction not possible.")

# --------- Vergleich Bundesländer & Education (Ampel) --------
if dropout is not None and not pd.isnull(dropout):
    comp_states = (
        df[
            (df["year"] == int(year))
            & (df["sector"] == sector)
            & (df["education"] == education)
            & (df["age"] == age)
        ]
        .groupby("state")["dropout_rate"]
        .mean()
        .sort_values()
        .reset_index()
    )
    better_states = comp_states[comp_states["dropout_rate"] < dropout].tail(5)
    worse_states = comp_states[comp_states["dropout_rate"] > dropout].head(5)

    st.markdown("<br><b>Dropout Risk by Federal State</b>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (lbl, dr) in enumerate(better_states.values):
        cols[i].markdown(f"<div class='ampel-green'>{lbl}<br>{dr*100:.1f}%</div>", unsafe_allow_html=True)
    for i, (lbl, dr) in enumerate(worse_states.values):
        cols[i].markdown(f"<div class='ampel-red'>{lbl}<br>{dr*100:.1f}%</div>", unsafe_allow_html=True)

    # Vergleich Education
    comp_edu = (
        df[
            (df["year"] == int(year))
            & (df["sector"] == sector)
            & (df["state"] == state)
            & (df["age"] == age)
        ]
        .groupby("education")["dropout_rate"]
        .mean()
        .sort_values()
        .reset_index()
    )
    better_edu = comp_edu[comp_edu["dropout_rate"] < dropout].tail(2)
    worse_edu = comp_edu[comp_edu["dropout_rate"] > dropout].head(2)

    st.markdown("<br><b>Dropout Risk by School Degree</b>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (lbl, dr) in enumerate(better_edu.values):
        cols[i].markdown(f"<div class='ampel-green'>{lbl}<br>{dr*100:.1f}%</div>", unsafe_allow_html=True)
    for i, (lbl, dr) in enumerate(worse_edu.values):
        cols[i+2].markdown(f"<div class='ampel-red'>{lbl}<br>{dr*100:.1f}%</div>", unsafe_allow_html=True)

# ------- Show all features button -------
if show_features:
    filter_mask = (
        (df["state"] == state)
        & (df["sector"] == sector)
        & (df["education"] == education)
        & (df["age"] == age)
        & (df["year"] == int(year))
    )
    st.markdown("<br><b>All Features for your Selection</b>", unsafe_allow_html=True)
    st.dataframe(df[filter_mask].reset_index(drop=True))