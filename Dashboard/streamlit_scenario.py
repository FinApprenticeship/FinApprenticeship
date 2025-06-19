import streamlit as st
import pandas as pd
import plotly.express as px
import re # For regular expression parsing of column names
import os

# st.set_page_config(layout="wide", page_title="Abbruchquote Szenario Analysen")

st.title("Abbruchquote Szenario Analysen")
st.markdown(
    """
    Diese interaktive Analyse zeigt die Entwicklung der Abbruchquote über die Jahre hinweg.
    Wählen Sie verschiedene Szenarien, Effektgrößen und Regionen aus, um deren Auswirkungen
    zu visualisieren und mit dem Basis-Szenario zu vergleichen.
    """
)

# --- Dictionaries ---
SCOPES = {
    'bund': 'Bund',
    'hh': 'Hamburg',
    "bw": "Baden-Württemberg",
    "by": "Bayern",
    "be": "Berlin",
    "bb": "Brandenburg",
    "hb": "Bremen",
    "he": "Hessen",
    "mv": "Mecklenburg-Vorpommern",
    "ni": "Niedersachsen",
    "nw": "Nordrhein-Westfalen",
    "rp": "Rheinland-Pfalz",
    "sl": "Saarland",
    "sn": "Sachsen",
    "st": "Sachsen-Anhalt",
    "sh": "Schleswig-Holstein",
    "th": "Thüringen"
}

SCENARIO_DISPLAY_NAMES = {
    'BAU': 'Basis',
    'EDU': 'Bildung',
    'UNEMP': 'Arbeitslosigkeit',
    'WAGE': 'Löhne'
}

script_dir = os.path.dirname(__file__)

csv_file_path = os.path.join(script_dir, 'data', 'scenario_analysis_results.csv.bz2')


# --- Data Loading and Preprocessing (cached for performance) ---
@st.cache_data
def load_and_preprocess_data(file_path, scopes_dict, scenario_names_dict):
    """
    Loads the CSV data, preprocesses column names, and returns a long-format DataFrame
    along with unique filter options, separating the 'Basis' scenario.
    """
    try:
        df = pd.read_csv(file_path)
        st.success("Daten erfolgreich geladen!")
    except FileNotFoundError:
        st.error(f"Error: '{os.path.basename(file_path)}' not found at '{file_path}'. Please ensure the file is in the correct directory.")
        st.stop()

    if 'year' not in df.columns:
        st.error("Error: 'year' column not found in the dataset. Please ensure your CSV has a 'year' column.")
        st.stop()

    scenario_cols = [col for col in df.columns if col != 'year']
    parsed_data = []

    col_name_pattern = re.compile(r'^(?P<Szenario>[A-Z]+)(?P<EffectSize>[+-]?\d+)?(?:_?(?P<Region>[A-Z]+))?_proportion_ones$')

    for col in scenario_cols:
        match = col_name_pattern.match(col)
        if match:
            szenario = match.group('Szenario')
            effect_size_str = match.group('EffectSize')
            region_code = match.group('Region')

            display_scenario = scenario_names_dict.get(szenario, szenario)

            display_effect_size = "Base"
            if effect_size_str is not None:
                display_effect_size = f"{int(effect_size_str)}%"

            display_region = "Overall"
            if region_code is not None:
                if region_code.lower() == 'all':
                    display_region = scopes_dict['bund']
                elif region_code.lower() in scopes_dict:
                    display_region = scopes_dict[region_code.lower()]
                else:
                    display_region = region_code


            for index, row in df.iterrows():
                parsed_data.append({
                    'year': row['year'],
                    'Abbruchquote': row[col],
                    'Scenario': display_scenario,
                    'Effect Size': display_effect_size,
                    'Region': display_region,
                    'Original Column': col
                })
        else:
            pass


    if not parsed_data:
        st.error("No scenario data columns found matching the expected pattern. Please check your column names or the regex pattern.")
        st.stop()

    df_long = pd.DataFrame(parsed_data)

    basis_scenario_display_name = scenario_names_dict['BAU']

    basis_scenario_df_all_regions = df_long[
        (df_long['Scenario'].str.strip() == basis_scenario_display_name) &
        (df_long['Effect Size'].str.strip() == 'Base')
    ].copy()

    df_long_filtered_for_selection = df_long[
        ~((df_long['Scenario'].str.strip() == basis_scenario_display_name) &
          (df_long['Effect Size'].str.strip() == 'Base'))
    ].copy()

    all_scenarios = sorted(df_long_filtered_for_selection['Scenario'].unique().tolist())
    all_effect_sizes = sorted(df_long_filtered_for_selection['Effect Size'].unique().tolist())
    all_regions = sorted(df_long_filtered_for_selection['Region'].unique().tolist())

    return df_long, basis_scenario_df_all_regions, all_scenarios, all_effect_sizes, all_regions

# Load data and get filter options
df_long_full, basis_scenario_df_all_regions, all_scenarios, all_effect_sizes, all_regions = load_and_preprocess_data(csv_file_path, SCOPES, SCENARIO_DISPLAY_NAMES)


# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filteroptionen")

    show_basis_scenario = st.checkbox("Basis-Szenario anzeigen", value=True)
    st.markdown("---")

    all_scenarios_options = ["Alle"] + all_scenarios
    selected_scenarios = st.multiselect(
        "Auswahl Szenario(s):",
        options=all_scenarios_options,
        default=["Alle"] if "Alle" in all_scenarios_options else []
    )
    if "Alle" in selected_scenarios:
        selected_scenarios_filtered = all_scenarios
    else:
        selected_scenarios_filtered = selected_scenarios


    all_effect_sizes_options = ["Alle"] + all_effect_sizes
    selected_effect_sizes = st.multiselect(
        "Auswahl Effektgröße(n):",
        options=all_effect_sizes_options,
        default=["Alle"] if "Alle" in all_effect_sizes_options else []
    )
    if "Alle" in selected_effect_sizes:
        selected_effect_sizes_filtered = all_effect_sizes
    else:
        selected_effect_sizes_filtered = selected_effect_sizes


    all_regions_options = ["Alle"] + all_regions
    selected_regions = st.multiselect(
        "Auswahl Region(en):",
        options=all_regions_options,
        default=["Alle"] if "Alle" in all_regions_options else []
    )
    if "Alle" in selected_regions:
        selected_regions_filtered = all_regions
    else:
        selected_regions_filtered = selected_regions

    st.markdown('### Ausgewählte Filter:\n')
    st.markdown('**Szenario(s):**\n' + '\n'.join([f' - {s}' for s in selected_scenarios_filtered]))
    st.markdown('**Effektgröße(n):**\n' + '\n'.join([f' - {es}' for es in selected_effect_sizes_filtered]))
    st.markdown('**Region(en):**\n' + '\n'.join([f' - {r}' for r in selected_regions_filtered]))


# --- Filter Data Based on Selections ---
filtered_df = df_long_full[
    (df_long_full['Scenario'].isin(selected_scenarios_filtered)) &
    (df_long_full['Effect Size'].isin(selected_effect_sizes_filtered)) &
    (df_long_full['Region'].isin(selected_regions_filtered))
].copy()

if show_basis_scenario:
    filtered_basis_df_for_display = basis_scenario_df_all_regions[
        basis_scenario_df_all_regions['Region'].isin(selected_regions_filtered)
    ].copy()
    combined_df = pd.concat([filtered_df, filtered_basis_df_for_display]).drop_duplicates().copy()
else:
    combined_df = filtered_df.copy()

if combined_df.empty:
    st.info("Keine Daten für die ausgewählten Filter gefunden. Bitte passen Sie Ihre Auswahl an oder aktivieren Sie 'Basis-Szenario anzeigen'.")
else:
    basis_scenario_name = SCENARIO_DISPLAY_NAMES.get('BAU', 'BAU')
    combined_df['Label'] = combined_df.apply(
        lambda row: f"{row['Scenario']} {row['Region']}" if row['Scenario'] == basis_scenario_name and row['Effect Size'] == 'Base'
        else f"{row['Scenario']} {row['Effect Size']} {row['Region']}", axis=1
    )

    fig = px.line(
        combined_df,
        x="year",
        y="Abbruchquote",
        color="Label", # Reverted to color by 'Label' for distinct lines
        title="Abbruchquote über Jahre nach Szenario, Effektgröße und Region",
        labels={
            "year": "Jahr",
            "Abbruchquote": "Abbruchquote (%)",
            "Region": "Region",
            "Label": "Szenario Details" # Legend label
        },
        hover_data={
            "Scenario": True,
            "Effect Size": True,
            "Region": True,
            "Label": True,
            "Abbruchquote": ":.2%"
        }
    )

    fig.update_layout(
        hovermode="x unified",
        legend_title_text="Szenario Details", # Reverted legend title
        xaxis_title="Jahr",
        yaxis_title="Abbruchquote (%)",
        # plot_bgcolor="black",
        # paper_bgcolor="black",
        # font=dict(family="Inter", size=12, color="white"),
        font=dict(family="Inter", size=12),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#FFFFFF", tickformat=".0%", range=[combined_df['Abbruchquote'].min()*0.9, combined_df['Abbruchquote'].max()*1.1])
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#FFFFFF", tickmode='linear', dtick=1)


    st.plotly_chart(fig, use_container_width=True)

    # --- Short description of items below the graph ---
    st.markdown("---")
    st.markdown("### Erläuterungen zu den Szenarien und Kategorien:")
    st.markdown("""
    * **Szenarien:**
        * **Basis**: Das unveränderte Basisszenario ("Business As Usual").
        * **Bildung**: Ein Szenario, das die Auswirkungen von Änderungen im Bereich 'Bildung' zeigt (Veränderung der Anteile an Bildungsabschlüssen).
        * **Arbeitslosigkeit**: Ein Szenario, das die Auswirkungen von Änderungen im Bereich 'Arbeitslosigkeit' zeigt (Veränderung der Arbeitslosenquote).
        * **Löhne**: Ein Szenario, das die Auswirkungen von Änderungen im Bereich 'Löhne' zeigt (Veränderung des Nominallohnindexes).
    * **Effektgröße:** Beschreibt die prozentuale Veränderung des jeweiligen Szenarios pro Jahr (z.B. "Bildung 1%" entspricht das jeweils 1% der Personen einen höheren Bildungsabschluss erzielt haben).
    * **Region:** Zeigt die Ergebnisse für die ausgewählten Regionen in Deutschland (Bundesländer oder Bund).
    """)

    # --- Data Export Feature ---
    st.markdown("---")
    st.subheader("Datenexport")
    csv_export = combined_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Angezeigte Daten herunterladen (CSV)",
        data=csv_export,
        file_name="abbruchquote_szenario_analyse.csv",
        mime="text/csv",
    )

    # --- Summary Statistics Table ---
    st.markdown("---")
    st.subheader("Zusammenfassende Statistiken")

    if not combined_df.empty:
        summary_stats = combined_df.groupby(['Region', 'Label'])['Abbruchquote'].agg(['mean', 'std', 'min', 'max']).reset_index()
        summary_stats.columns = ['Region', 'Szenario Details', 'Mittelwert', 'Standardabweichung', 'Minimum', 'Maximum']
        # Format numerical columns as percentages for better readability
        summary_stats['Mittelwert'] = summary_stats['Mittelwert'].map('{:.2%}'.format)
        summary_stats['Standardabweichung'] = summary_stats['Standardabweichung'].map('{:.2%}'.format)
        summary_stats['Minimum'] = summary_stats['Minimum'].map('{:.2%}'.format)
        summary_stats['Maximum'] = summary_stats['Maximum'].map('{:.2%}'.format)

        st.dataframe(summary_stats, use_container_width=True)
    else:
        st.info("Keine Daten zum Anzeigen von Statistiken.")
