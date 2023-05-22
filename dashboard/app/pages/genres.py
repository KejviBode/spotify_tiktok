# from os import path
# from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import plotly.express as px
# import pandas as pd

# from helper_functions import conn

# register_page(__name__, path="/genres")

# layout = html.Main([html.Div(style={"margin-top": "100px"}),
#     html.H1("Genres", style={'color': 'Black'}),
#                     dcc.Dropdown(["All", "Spotify", "Tiktok"], id="genre-dropdown", placeholder="Choose One"),
#                     dcc.Graph(id="genre-graph")])

# @callback(Output(component_id="genre-graph", component_property="figure"),
#           Input("genre-dropdown", "value"))
# def song_attribute_bar_chart(user_input):
#     pass