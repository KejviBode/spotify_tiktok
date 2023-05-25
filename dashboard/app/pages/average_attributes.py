from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

from helper_functions import conn, danceability, energy, valence, tempo, speechiness

register_page(__name__, path="/average_attributes")

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Average Attributes", style={'color': 'Black'}),
                    dcc.Dropdown(["All", "Spotify", "Tiktok"], id="attribute-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="attribute-graph"),
    html.Div([html.H2("Track Attributes Key:"),
        html.Ul(
            children=[
                html.Li([html.Strong("Danceability"), " - ", danceability], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Energy"), " - ", energy], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Valence"), " - ", valence], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Tempo"), " - ", tempo], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Speechiness"), " - ", speechiness], style={'margin-bottom': '5px'})
            ]
        )], style={'margin-left': '80px', 'margin-right': '80px'})])


@callback(Output(component_id="attribute-graph", component_property="figure"),
          Input("attribute-dropdown", "value"))
def attribute_bar_chart(user_input):
    '''
    Creates a bar chart of the average attributes across all songs
    '''
    with conn, conn.cursor() as cur:
        if user_input == "All" or user_input == None:
            sql_input = '''
            SELECT
                'In Spotify Charts' AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_speechiness) AS avg_speechiness,
                AVG((track_tempo - 50)/200) AS avg_tempo
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
                AVG(track_speechiness) AS avg_speechiness,
                AVG((track_tempo - 50)/200) AS avg_tempo
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
                graph_dict["Tempo"] = results[x][5]
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
                    AVG(track_speechiness) AS avg_speechiness,
                    AVG((track_tempo - 50)/200) AS avg_tempo
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
                graph_dict["Tempo"] = results[x][5]
                graph_dicts.append(graph_dict)
            
            graph_dict = {}
            graph_dict["name"] = "Both"
            graph_dict["Danceability"] = (results[1][1] + results[2][1])/2
            graph_dict["Energy"] = (results[1][2] + results[2][2])/2
            graph_dict["Valence"] = (results[1][3] + results[2][3])/2
            graph_dict["Speechiness"] = (results[1][4] + results[2][4])/2
            graph_dict["Tempo"] = (results[1][5] + results[1][5])/2
            graph_dicts.append(graph_dict)

        colours = ['#1ed760', '#000000', '#00f2ea', '#ffffff', '#ff0050']


        fig_px = px.bar(graph_dicts, x='name', y=['Danceability', 'Energy', 'Valence', 'Speechiness', 'Tempo'], barmode='group', title='Bar Chart')
        fig_px.update_layout(xaxis_title="Track Attributes", yaxis_title="Value", title="", legend=dict(title='Attributes'))
        fig_px.update_yaxes(range=[0, 1])

        fig_go = go.Figure(fig_px.to_dict())

        for i, colour in enumerate(colours):
            fig_go.data[i].marker.color = colour

    fig_go.update_layout(
        xaxis_title="Track Attributes",
        yaxis_title="Value",
        title="",
        legend=dict(title='Attributes'),
        plot_bgcolor='#bfbdbd'
    )
    return fig_go
