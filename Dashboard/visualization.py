import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Load German GeoJSON data
@st.cache_data
def load_german_states_geojson():
    # URL for German states GeoJSON
    url = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json"
    response = requests.get(url)
    return response.json()

# Daten laden
@st.cache_data
def load_dataframe():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'dazubi_grouped_berufe.csv')
    df = pd.read_csv(csv_path, index_col=0)

    # We need the plain state names to use them as keys in the map
    # Berlin is our only special case
    STATE_NAME_MAPPING = {
        "Berlin (ab 1991 mit Berlin-Ost)": "Berlin"
    }
    df['Region_key'] = df['Region'].map(lambda x: STATE_NAME_MAPPING.get(x, x))
    return df

@st.cache_data
def load_data(df):
    attributes = [x for x in df.columns if x not in ['Region', 'Region_key', 'Beruf_clean', 'Jahr']]
    return {
        'states': df['Region'].unique(),
        'jobs': df['Beruf_clean'].unique(),
        'years': df['Jahr'].unique(),
        'attributes': attributes
    }

def app():
    df = load_dataframe()
    data = load_data(df)
    type_analysis = 'Zeitreihe'
    selected_states = []
    selected_years = []
    selected_jobs = []
    selected_attributes = []

    # Load GeoJSON data
    germany_geojson = load_german_states_geojson()

    with st.sidebar:
        # We need at least one attribute to do anything - so it should be the first box in the sidebar
        all_attributes = ["Alle"] + sorted(data['attributes'])
        selected_attributes = st.multiselect("Merkmal", all_attributes, placeholder="Wähle Merkmale aus")
        if "Alle" in selected_attributes:
            selected_attributes = sorted(data['attributes'])

        # For Zeitreihen we can select a state, but not a year - because we show all years in a line chart
        # For Karte we can select a year, but not a state - because we show all states in a map
        type_analysis = st.radio('Visualisierungstyp', ['Zeitreihe', 'Karte'], index=0)

        if type_analysis == 'Zeitreihe':
            all_states = ["Alle"] + sorted(data['states'])
            selected_states = st.multiselect("Bundesland", all_states, placeholder="Wähle Bundesländer aus")
            if "Alle" in selected_states:
                selected_states = sorted(data['states'])
        elif type_analysis == 'Karte':
            all_years = ["Alle"] + sorted(data['years'])
            selected_years = st.multiselect("Jahr", all_years, placeholder="Wähle Jahre aus")
            if "Alle" in selected_years:
                selected_years = sorted(data['years'])

        all_jobs = ["Alle"] + sorted(data['jobs'])
        selected_jobs = st.multiselect("Beruf", all_jobs, placeholder="Wähle Berufe aus")
        if "Alle" in selected_jobs:
            selected_jobs = sorted(data['jobs'])

        # Show the selected values, beause the multiselect cuts off the values, if they are too long
        st.markdown('### Ausgewählte Bundesländer:\n'
                    + '\n'.join([f'  * {state}' for state in selected_states])
                    + '\n### Ausgewählte Jahre:\n'
                    + '\n'.join([f'  * {year}' for year in selected_years])
                    + '\n### Ausgewählte Berufe:\n'
                    + '\n'.join([f'  * {job}' for job in selected_jobs])
                    + '\n### Ausgewählte Merkmale:\n'
                    + '\n'.join([f'  * {attribute}' for attribute in selected_attributes])
                    )

    st.title("🚦 Visualisierung der bibb DAZUBI Daten")

    # We need at least one attribute to do anything
    if len(selected_attributes) > 0:
        df_grouped = df
        # At first filter the dataframe based on the selected years, states, jobs, and attributes
        if type_analysis == 'Bundesland' and len(selected_years) > 0:
            df_grouped = df_grouped[df_grouped['Jahr'].isin(selected_years)]
        if type_analysis == 'Zeitreihe' and len(selected_states) > 0:
            df_grouped = df_grouped[df_grouped['Region'].isin(selected_states)]
        if len(selected_jobs) > 0:
            df_grouped = df_grouped[df_grouped['Beruf_clean'].isin(selected_jobs)] 

        if type_analysis == 'Zeitreihe':
            # What should happen, if we have more than one state and more than one job?
            if len(selected_states) > 1:
                # If we have more than one state, we show a line chart per state
                df_grouped = df_grouped.groupby(['Jahr', 'Region'])
                for attribute in selected_attributes:
                    df_attr = df_grouped[attribute].sum().reset_index()
                    fig = px.line(df_attr, x='Jahr', y=attribute, color='Region', labels={'variable': 'Ausgewählte Bundesländer'})
                    fig.update_layout(xaxis=dict(tickformat='d'))
                    st.plotly_chart(fig, use_container_width=True)
            elif len(selected_jobs) > 1:
                # If we have more than one job, we show a line chart per job
                df_grouped = df_grouped.groupby(['Jahr', 'Beruf_clean'])
                for attribute in selected_attributes:
                    df_attr = df_grouped[attribute].sum().reset_index()
                    fig = px.line(df_attr, x='Jahr', y=attribute, color='Beruf_clean', labels={'variable': 'Ausgewählte Berufe'})
                    fig.update_layout(xaxis=dict(tickformat='d'))
                    st.plotly_chart(fig, use_container_width=True)
            else: 
                # We have no selected states or jobs, so we show a line chart for the selected attributes
                df_grouped = df_grouped.groupby(['Jahr'])[selected_attributes].sum().reset_index()
                fig = px.line(df_grouped, x='Jahr', y=selected_attributes, labels={'variable': 'Ausgewählte Merkmale'})
                fig.update_layout(xaxis=dict(tickformat='d'))
                st.plotly_chart(fig, use_container_width=True)
        elif type_analysis == 'Karte':
            # We have no selected years, so we show a map for the selected attributes
            # We group by Region and Region_key, so we can use Region_key as the key in the map and Region for the hover text
            df_grouped = df_grouped.groupby(['Region', 'Region_key'])[selected_attributes].sum().reset_index()
            
            # Create the choropleth map for German states
            fig = px.choropleth(
                df_grouped,
                locations='Region_key',
                geojson=germany_geojson,
                featureidkey='properties.name',
                color=selected_attributes[0],
            )
            
            # Add custom hover text with full state names
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>" +
                            f"{selected_attributes[0]}: %{{z:,.0f}}",
                customdata=df_grouped[['Region']].values
            )
            
            # Update layout for better visualization
            fig.update_geos(
                fitbounds="locations",
                visible=False
            )
            fig.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                # plotly has troubles with localizations, but at the moment we only support German, so we set the separators by hand
                separators=",.",
                geo=dict(
                    scope='europe',
                    center=dict(lat=51.1657, lon=10.4515),
                    projection_scale=6
                )
            )
            
            # Update colorbar to use German number format
            fig.update_coloraxes(
                colorbar=dict(
                    tickformat=",.0f",
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)


    st.caption("Made with ❤️ by your Data Science Team FinApprenticeship")
