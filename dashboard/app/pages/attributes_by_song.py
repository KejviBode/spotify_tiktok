# from os import path
# from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import plotly.express as px
# import pandas as pd

# from helper_functions import conn

# register_page(__name__, path="/attributes_by_song")

# layout = html.Main([html.Div(style={"margin-top": "100px"}),
#     html.H1("Attributes by song", style={'color': 'Black'}),
#                     dcc.Dropdown(["All", "Spotify", "Tiktok"], id="song-dropdown", placeholder="Choose One"),
#                     dcc.Graph(id="song-attribute-graph")])

# @callback(Output(component_id="song-attribute-graph", component_property="figure"),
#           Input("song-dropdown", "value"))
# def song_attribute_bar_chart(user_input):
#     pass