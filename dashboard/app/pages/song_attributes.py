from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import pandas as pd

from helper_functions import conn, get_top_ten

register_page(__name__, path="/song_attributes")

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Song Attributes", style={'color': 'Black'}),
                    dcc.Dropdown(["All", "Spotify", "Tiktok"], id="attribute-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="attribute-graph")])


@callback(Output(component_id="attribute-graph", component_property="figure"),
          Input("attribute-dropdown", "value"))
def attribute_bar_chart(user_input):
    latest_records = plant_data.loc[plant_data.groupby('plant_id')['recording_taken'].idxmax()]

    if user_input == "All":
        latest_data = latest_records
    else:
        latest_data = latest_records[latest_records["last_name"] == user_input]

    fig = px.bar(latest_data, x='name', y='soil_moisture', title='Temperatures by Plant', color="name", color_discrete_sequence=px.colors.qualitative.Light24)
    fig = fig.update_layout(xaxis_title='Plant', yaxis_title='Soil Moisture Level', showlegend=False, plot_bgcolor='white', yaxis=dict(gridcolor='grey'))
    return fig