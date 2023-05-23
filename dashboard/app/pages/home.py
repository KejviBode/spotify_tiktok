from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import pandas as pd

from helper_functions import conn, get_top_ten

register_page(__name__, path="/")


spotify_top_ten = get_top_ten("spotify", conn)
tiktok_top_ten = get_top_ten("tiktok", conn)

spotify_data = pd.DataFrame(spotify_top_ten)
tiktok_data = pd.DataFrame(tiktok_top_ten)

layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("Today's Charts", style={'color': 'Black'}),
    dcc.Interval(id="interval-component", interval=60 * 1000, n_intervals=0),
    html.Div(id="charts-container")])


@callback(Output("charts-container", "children"),
              Input("interval-component", "n_intervals"))
def update_charts(n):
    spotify_top_ten = get_top_ten("spotify", conn)
    tiktok_top_ten = get_top_ten("tiktok", conn)

    spotify_data = pd.DataFrame(spotify_top_ten)
    tiktok_data = pd.DataFrame(tiktok_top_ten)

    spotify_table = dash_table.DataTable(
        id="spotify-table",
        columns=[
            {"name": "Song", "id": "track_name"},
            {"name": "Artist", "id": "spotify_names"},
            {"name": "Spotify Rank", "id": "spotify_rank"},
            {"name": "TikTok Rank", "id": "tiktok_rank"}
        ],
        data=spotify_data.to_dict("records"),
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#CDCBCD",
            "text-decoration": 'underline'
        },
        style_cell={
            "textAlign": "left",
            "fontWeight": "bold",
            "maxWidth": "200px",
            "whiteSpace": "normal"
        },
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#1ed760'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'white'
        }
    ]
    )

    tiktok_table = dash_table.DataTable(
        id="tiktok-table",
        columns=[
            {"name": "Song", "id": "track_name"},
            {"name": "Artist", "id": "spotify_names"},
            {"name": "TikTok Rank", "id": "tiktok_rank"},
            {"name": "Spotify Rank", "id": "spotify_rank"}
        ],
        data=tiktok_data.to_dict("records"),
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#CDCBCD",
            "text-decoration": 'underline'
        },
        style_cell={
            "textAlign": "left",
            "fontWeight": "bold",
            "maxWidth": "200px",
            "whiteSpace": "normal"
        },
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(255, 0, 80, 0.2)'
        },
        {
            'if': {'row_index': 'even'},
            'backgroundColor': 'rgb(0, 242, 234, 0.2)'
        }
    ]
    )

    return html.Div([
        html.Div([
            html.H3("Spotify Top 10"),
            spotify_table
        ], className="table-container"),
        html.Div([
            html.H3("TikTok Top 10"),
            tiktok_table
        ], className="table-container"),
    ], style={"marginLeft": "100px", "marginRight": "100px", "marginBottom": "50px"})
