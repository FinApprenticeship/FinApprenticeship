import plotly.graph_objects as go
import plotly.express as px

def apply_common_layout_settings(fig, number_format=None, number_format_x=None, number_format_y=None, font_size_title=18, font_size_base=16):
    """
    Apply consistent layout and formatting settings to a Plotly figure.

    For possible values of number_format, number_format_x, and number_format_y, see:
        - https://plotly.com/python/tick-formatting/ (general tick formatting)
        - https://github.com/d3/d3-format (d3-format reference used by Plotly)
        - https://github.com/plotly/plotly.py/blob/master/doc/python/tick-formatting.md (Plotly tickformat docs)

    Args:
        fig: Plotly figure object to update.
        number_format: Format string for axis and colorbar ticks.
        number_format_x: Format string for x-axis ticks (overrides number_format).
        number_format_y: Format string for y-axis ticks (overrides number_format).
        font_size_title: Font size for axis titles.
        font_size_base: Base font size for chart text.
    """
    if number_format_x is None:
        number_format_x = number_format
    if number_format_y is None:
        number_format_y = number_format
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        # plotly has troubles with localizations, but at the moment we only support German, so we set the separators by hand
        separators=",.",
        font=dict(size=font_size_base),
        xaxis=dict(
            tickformat=number_format,
            title=dict(font=dict(size=font_size_title)),
            tickfont=dict(size=font_size_base)
        ),
        yaxis=dict(
            tickformat=number_format_y,
            title=dict(font=dict(size=font_size_title)),
            tickfont=dict(size=font_size_base)
        ),
        legend=dict(
            title=dict(
                font=dict(size=font_size_base)
            ),
            font=dict(
                size=font_size_base
            ),
        ),
        coloraxis=dict(
            colorbar=dict(
                tickformat=number_format,
                len=1, # Make the colorbar's height 100% of the chart's height
                y=0.5, # Center the colorbar vertically
                yanchor='middle', # Anchor the colorbar in the middle
                tickfont=dict(size=font_size_base)
            )
        ),
    ) 