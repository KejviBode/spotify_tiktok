from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd

from helper_functions import conn

register_page(__name__, path="/genres")

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Genres", style={'color': 'Black'}),
                    dcc.Dropdown(["All", "Spotify", "Tiktok"], id="genre-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="genre-graph")])

@callback(Output(component_id="genre-graph", component_property="figure"),
          Input("genre-dropdown", "value"))
def song_attribute_bar_chart(user_input):
    if user_input != "All" and user_input != None:
        sql_query = f"""
            SELECT g.genre_name, COUNT(ag.genre_id) AS genre_count
            FROM artist_genre ag
            JOIN genre g ON ag.genre_id = g.genre_id
            JOIN track_artist ta ON ag.artist_spotify_id = ta.artist_spotify_id
            JOIN track t ON ta.track_spotify_id = t.track_spotify_id
            WHERE t.in_{user_input.lower()} = true
            GROUP BY ag.genre_id, g.genre_name
            ORDER BY genre_count DESC
            LIMIT 20;
            """
    else:
        sql_query = "SELECT g.genre_name, COUNT(ag.genre_id) AS genre_count \
            FROM artist_genre ag \
            JOIN genre g ON ag.genre_id = g.genre_id \
            GROUP BY ag.genre_id, g.genre_name \
            ORDER BY genre_count DESC LIMIT 20;"
    
    df = pd.read_sql_query(sql_query, conn)
    fig = px.bar(df, x='genre_name', y='genre_count', title='Top 20 Genres')
    fig.update_layout(xaxis_title="Genres", yaxis_title="Count")
    return fig
