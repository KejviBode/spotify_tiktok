from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd

from helper_functions import conn, get_all_current_songs

register_page(__name__, path="/attributes_by_song")

songs = get_all_current_songs(conn)

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Attributes by song", style={'color': 'Black'}),
                    dcc.Dropdown(options=[{'label': song, 'value': song} for song in songs], id="song-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="song-attribute-graph")])

@callback(Output(component_id="song-attribute-graph", component_property="figure"),
          Input("song-dropdown", "value"))
def song_attribute_bar_chart(user_input):
    if user_input is None:
        fig = px.bar()
        fig.update_yaxes(range=[0, 1])
        return fig
    last_dash_index = user_input.rfind("-")
    song_name = user_input[:last_dash_index].strip()
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = f"SELECT track_danceability, track_energy, track_valence, \
            track_tempo, track_speechiness FROM track \
                WHERE track_name = '{song_name}'"
        cur.execute(sql_query)
        results = cur.fetchone()

    graph_dict = {}
    graph_dict["Danceability"] = results["track_danceability"]
    graph_dict["Energy"] = results["track_energy"]
    graph_dict["Valence"] = results["track_valence"]
    graph_dict["Speechiness"] = results["track_speechiness"]
    graph_dict["Tempo"] = (results["track_tempo"] - 50)/200

    if results is None:
        return px.bar()

    attribute_names = ['Danceability', 'Energy', 'Valence', 'Tempo', 'Speechiness']
    attribute_values = [graph_dict[attr] for attr in attribute_names]

    fig = px.bar(x=attribute_names, y=attribute_values)

    fig = px.bar(x=attribute_names, y=attribute_values, labels={'x': 'Attribute', 'y': 'Value'},
                 title=f'Song Attributes: {user_input}')
    fig.update_yaxes(range=[0, 1])
    return fig