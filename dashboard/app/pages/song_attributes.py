from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
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
    # if user_input == "All":
    #     return "All"
    # elif user_input == "Spotify":
    #     return "Spotify"
    with conn, conn.cursor() as cur:
        sql_input = '''
            SELECT
                CASE
                    WHEN in_spotify IS TRUE AND in_tiktok IS TRUE THEN 'In TikTok Charts'
                    WHEN in_spotify IS TRUE AND in_tiktok IS FALSE THEN 'Not in TikTok Charts'
                END AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_tempo) AS avg_tempo,
                AVG(track_speechiness) AS avg_speechiness
            FROM
                track
            GROUP BY
                situation
        '''
        cur.execute(sql_input)
        results = cur.fetchall()

    situations = [result[0] for result in results]
    attributes = ['Danceability', 'Energy', 'Valence', 'Tempo', 'Speechiness']
    averages = [[result[i] for result in results] for i in range(1, 6)]

    fig = px.bar(x=situations, y=averages, barmode='group', labels={'x': 'Situation', 'y': 'Average Value'}, title='Average Qualities by Situation')
    fig = fig.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(len(attributes))), ticktext=attributes), yaxis=dict(title='Average Value'))
    return fig
    # else:
    #     return "TikTok"

