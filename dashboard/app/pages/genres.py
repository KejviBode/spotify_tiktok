from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

from helper_functions import get_db_connection, conn, long_conn

register_page(__name__, path="/genres")

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Genres", style={'color': 'Black'}),
                    dcc.Dropdown(["All", "Spotify", "Tiktok"], id="genre-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="genre-graph")])

@callback(Output(component_id="genre-graph", component_property="figure"),
          Input("genre-dropdown", "value"))
def song_attribute_bar_chart(user_input):
    '''
    Creates a bar chart of the top 20 genres by count
    '''
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
    colours = ['#1ed760', '#000000', '#00f2ea', '#ffffff', '#ff0050']


    fig = go.Figure()

    for i, row in df.iterrows():
        color_index = i % len(colours)  # Calculate the index in the color_scheme list
        bar_color = colours[color_index]  # Get the color for the current bar
    
        fig.add_trace(go.Bar(
            x=[row['genre_name']],
            y=[row['genre_count']],
            marker_color=bar_color,
            name=row['genre_name'],
        ))

    fig.update_layout(
        xaxis_title="Genres",
        yaxis_title="Count",
        showlegend=False,
        title="Top 20 Genres",
        plot_bgcolor='#bfbdbd',
    )
    fig.update_yaxes(range=[0, 60])
    return fig
