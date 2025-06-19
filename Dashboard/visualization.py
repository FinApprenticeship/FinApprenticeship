import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests
from utils import apply_common_layout_settings, get_contrast_text_color

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
    df.rename(columns={'Beruf_clean': 'Beruf'}, inplace=True)
    # We need the plain state names to use them as keys in the map
    # Berlin is our only special case
    STATE_NAME_MAPPING = {
        "Berlin (ab 1991 mit Berlin-Ost)": "Berlin"
    }
    df['Region_key'] = df['Region'].map(lambda x: STATE_NAME_MAPPING.get(x, x))
    return df

@st.cache_data
def load_data(df):
    attributes = [x for x in df.columns if x not in ['Region', 'Region_key', 'Beruf', 'Jahr']]
    return {
        'states': df['Region'].unique(),
        'jobs': df['Beruf'].unique(),
        'years': df['Jahr'].unique(),
        'attributes': attributes
    }

colors_chart = px.colors.qualitative.Set1

def add_spike(fig, number_format, tickvals, attribute=None):
    if attribute is None:
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}: </b>" +
                        f"%{{y:{number_format}}}" +
                        '<extra></extra>'
        )
    else:
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>" +
                        f"{attribute}: %{{y:{number_format}}}" +
                        '<extra></extra>'
        )
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            showspikes=True,
            spikemode='across',
            spikesnap='data',
            spikethickness=1,
            spikedash='solid',
            spikecolor='white',
        ),
        hovermode='x',
    )
    for i, trace in enumerate(fig.data):
        color = colors_chart[i % len(colors_chart)]
        trace.hoverlabel.bgcolor = color
        trace.hoverlabel.font.color = get_contrast_text_color(color)


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
    number_format = ",.0f"
    if len(selected_attributes) > 0:
        df_filtered = df.copy()
        # At first filter the dataframe based on the selected years, states, jobs, and attributes
        if type_analysis == 'Bundesland' and len(selected_years) > 0:
            df_filtered = df_filtered[df_filtered['Jahr'].isin(selected_years)]
        if type_analysis == 'Zeitreihe' and len(selected_states) > 0:
            df_filtered = df_filtered[df_filtered['Region'].isin(selected_states)]
        if len(selected_jobs) > 0:
            df_filtered = df_filtered[df_filtered['Beruf'].isin(selected_jobs)] 

        if type_analysis == 'Zeitreihe':
            # What should happen, if we have more than one state and more than one job?
            if len(selected_states) > 1:
                # If we have more than one state, we show a line chart per state
                df_time = df_filtered.groupby(['Jahr', 'Region'])
                for attribute in selected_attributes:
                    df_attr = df_time[attribute].sum().reset_index()
                    # Define colors explicitly
                    fig = px.line(df_attr, x='Jahr', y=attribute, color='Region', 
                                labels={'variable': 'Ausgewählte Bundesländer'}, 
                                hover_name=None, hover_data=None,
                                color_discrete_sequence=colors_chart
                    )
                    apply_common_layout_settings(fig, number_format_x='d', number_format_y=number_format)
                    add_spike(fig, number_format, data['years'], attribute)
                    # Set hover label background to match trace color and text color for contrast
                    st.plotly_chart(fig, use_container_width=True)
            elif len(selected_jobs) > 1:
                # If we have more than one job, we show a line chart per job
                df_time = df_filtered.groupby(['Jahr', 'Beruf'])
                for attribute in selected_attributes:
                    df_attr = df_time[attribute].sum().reset_index()
                    fig = px.line(df_attr, x='Jahr', y=attribute, color='Beruf', labels={'variable': 'Ausgewählte Berufe'}, color_discrete_sequence=colors_chart)
                    apply_common_layout_settings(fig, number_format_x='d', number_format_y=number_format)
                    add_spike(fig, number_format, data['years'], attribute)
                    st.plotly_chart(fig, use_container_width=True)
            else: 
                # We have no selected states or jobs, so we show a line chart for the selected attributes
                df_time = df_filtered.groupby(['Jahr'])[selected_attributes].sum().reset_index()
                fig = px.line(df_time, x='Jahr', y=selected_attributes, labels={'variable': 'Ausgewählte Merkmale'}, color_discrete_sequence=colors_chart)
                fig.update_layout(yaxis_title='')
                apply_common_layout_settings(fig, number_format_x='d', number_format_y=number_format)
                add_spike(fig, number_format, data['years'])
                st.plotly_chart(fig, use_container_width=True)
        elif type_analysis == 'Karte':
            for attribute in selected_attributes:
                st.markdown(f'### {attribute}')
                col1, col2 = st.columns(2)
                with col1:
                    # We have no selected years, so we show a map for the selected attributes
                    # We group by Region and Region_key, so we can use Region_key as the key in the map and Region for the hover text
                    df_map = df_filtered.groupby(['Region', 'Region_key'])[attribute].sum().reset_index()
                    
                    # Create the choropleth map for German states
                    fig = px.choropleth(
                        df_map,
                        locations='Region_key',
                        geojson=germany_geojson,
                        featureidkey='properties.name',
                        color=attribute,
                        color_continuous_scale='PuBu'
                    )
                    
                    # Add custom hover text with full state names
                    fig.update_traces(
                        hovertemplate="<b>%{customdata[0]}</b><br>" +
                                    f"{attribute}: %{{z:{number_format}}}",
                        customdata=df_map[['Region']].values
                    )
                    
                    # Update layout for better visualization
                    fig.update_geos(
                        fitbounds="locations",
                        visible=False
                    )
                    apply_common_layout_settings(fig, number_format)
                    fig.update_layout(
                        geo=dict(
                            scope='europe',
                            center=dict(lat=51.1657, lon=10.4515),
                            projection_scale=6
                        ),
                    )
                    event_map = st.plotly_chart(fig, use_container_width=True, on_select='rerun')

                with col2:
                    state = None
                    df_map_filtered = df_filtered.copy()
                    if len(event_map.get('selection', {}).get('points', [])) > 0:
                        state = event_map.get('selection', {}).get('points', [])[0]['location']
                        if state is not None:
                            df_map_filtered = df_map_filtered[df_map_filtered['Region_key'] == state]
                    df_bar = df_map_filtered.groupby(['Beruf'])[attribute].sum().sort_values(ascending=False).reset_index()
                    # take the top 15 and reverse the order, so the bar chart shows the longest at the top
                    df_bar = df_bar.head(15)[::-1]
                    # fig = px.bar(df_bar, x=attribute, y='Beruf', text_auto=True, orientation='h', height=len(df_bar) * 40)
                    # Use GraphObj instead of express, because we can set the position of the text inside the bar
                    fig = go.Figure(go.Bar(
                        x=df_bar[attribute],
                        y=df_bar['Beruf'],
                        text=df_bar[attribute].tolist(),
                        orientation='h',
                        textposition='inside',
                        insidetextanchor='start',
                        texttemplate=f'%{{text:{number_format}}}'
                    ))
                    fig.update_traces(
                        hoverinfo='none'
                    )
                    apply_common_layout_settings(fig, number_format)
                    fig.update_layout(
                        height=len(df_bar) * 40,
                        xaxis=dict(
                            title=attribute,
                            showgrid=True
                        ),
                        yaxis=dict(
                            showgrid=False
                        ),
                    )
                    st.plotly_chart(fig, use_container_width=True)

app()