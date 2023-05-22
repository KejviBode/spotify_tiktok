from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd

from helper_functions import conn

register_page(__name__, path="/average_song_attributes")

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Average Song Attributes", style={'color': 'Black'}),
                    dcc.Dropdown(["All", "Spotify", "Tiktok"], id="attribute-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="attribute-graph")])


@callback(Output(component_id="attribute-graph", component_property="figure"),
          Input("attribute-dropdown", "value"))
def attribute_bar_chart(user_input):
    with conn, conn.cursor() as cur:
        if user_input == "All":
            sql_input = '''
            SELECT
                'In Spotify Charts' AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_speechiness) AS avg_speechiness
            FROM
                track
            WHERE
                in_spotify IS TRUE
            GROUP BY
                situation

            UNION

            SELECT
                'In TikTok Charts' AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_speechiness) AS avg_speechiness
            FROM
                track
            WHERE
                in_tiktok IS TRUE
            GROUP BY
                situation
            '''
            cur.execute(sql_input)
            results = cur.fetchall()

            graph_dicts = []
            for x in range (2):
                graph_dict = {}
                graph_dict["name"] = results[x][0]
                graph_dict["Danceability"] = results[x][1]
                graph_dict["Energy"] = results[x][2]
                graph_dict["Valence"] = results[x][3]
                graph_dict["Speechiness"] = results[x][4]
                graph_dicts.append(graph_dict)
        else:
            if user_input == "Spotify":
                comparison = "TikTok"
            else:
                user_input = "TikTok"
                comparison = "Spotify"

            sql_input = f'''
                SELECT
                    CASE
                        WHEN in_{user_input.lower()} IS TRUE AND in_{comparison.lower()} IS TRUE THEN 'In {comparison} Charts'
                        WHEN in_{user_input.lower()} IS TRUE AND in_{comparison.lower()} IS FALSE THEN 'Not in {comparison} Charts'
                    END AS situation,
                    AVG(track_danceability) AS avg_danceability,
                    AVG(track_energy) AS avg_energy,
                    AVG(track_valence) AS avg_valence,
                    AVG(track_speechiness) AS avg_speechiness
                FROM
                    track
                GROUP BY
                    situation
            '''
            cur.execute(sql_input)
            results = cur.fetchall()

            graph_dicts = []
            for x in range (1, 3):
                graph_dict = {}
                graph_dict["name"] = results[x][0]
                graph_dict["Danceability"] = results[x][1]
                graph_dict["Energy"] = results[x][2]
                graph_dict["Valence"] = results[x][3]
                graph_dict["Speechiness"] = results[x][4]
                graph_dicts.append(graph_dict)
            
            graph_dict = {}
            graph_dict["name"] = "Both"
            graph_dict["Danceability"] = (results[1][1] + results[2][1])/2
            graph_dict["Energy"] = (results[1][2] + results[2][2])/2
            graph_dict["Valence"] = (results[1][3] + results[2][3])/2
            graph_dict["Speechiness"] = (results[1][4] + results[2][4])/2
            graph_dicts.append(graph_dict)

        fig = px.bar(graph_dicts, x='name', y=['Danceability', 'Energy', 'Valence', 'Speechiness'], barmode='group', title='Bar Chart')
        return fig
