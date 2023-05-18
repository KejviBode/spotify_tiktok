from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output

register_page(__name__, path="/")

layout = html.Main([html.H2("Welcome to the Spotify/TikTok Chart Comparison Dashboard!", style={'color': 'Black'})]
)