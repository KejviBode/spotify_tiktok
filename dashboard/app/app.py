from os import path

from dash import Dash, html, dcc, callback, Input, Output, page_registry, page_container
import plotly.express as px
import pandas as pd


app = Dash(__name__, use_pages=True)


app.layout = html.Div(
    [html.Nav([dcc.Link(page["name"], href=page["path"], style={'margin-right': '20px', 'color': 'blue'}) for page in page_registry.values()]),
    html.H1("Spotify/TikTok Chart Comparison", style={'color': 'black'}),
     page_container]
)