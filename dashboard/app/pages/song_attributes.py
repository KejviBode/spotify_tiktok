from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from psycopg2.extras import RealDictCursor

from helper_functions import conn, get_all_current_songs, danceability, energy, valence, tempo, speechiness

register_page(__name__, path="/song_attributes")

songs = get_all_current_songs(conn)


layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Song Attributes", style={'color': 'Black'}),
                    dcc.Dropdown(options=[{'label': song, 'value': song} for song in songs], id="song-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="song-attribute-graph"),
    html.Div([html.H2("Track Attributes Key:"),
        html.Ul(
            children=[
                html.Li([html.Strong("Danceability"), " - ", danceability], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Energy"), " - ", energy], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Valence"), " - ", valence], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Tempo"), " - ", tempo], style={'margin-bottom': '5px'}),
                html.Li([html.Strong("Speechiness"), " - ", speechiness], style={'margin-bottom': '5px'})
            ]
        )], style={'margin-left': '80px', 'margin-right': '80px'})
    ])

@callback(Output(component_id="song-attribute-graph", component_property="figure"),
          Input("song-dropdown", "value"))
def song_attribute_bar_chart(user_input):
    '''
    Creates bar graph of attributes for song from user input
    '''
    if user_input is None:
        fig = px.bar()
        fig.update_layout(xaxis_title="Track Attributes", yaxis_title="Value", title="Please choose a song", plot_bgcolor='#bfbdbd')
        fig.update_yaxes(range=[0, 1])
        return fig
    last_dash_index = user_input.rfind("-")
    song_name = user_input[:last_dash_index].strip()
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT track_danceability, track_energy, track_valence, \
            track_tempo, track_speechiness FROM track \
                WHERE track_name = %s"
        cur.execute(sql_query, (song_name,))
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
    colours = ['#1ed760', '#000000', '#00f2ea', '#000000', '#ff0050']


    fig = go.Figure(data=[
    go.Bar(x=attribute_names, y=attribute_values, marker=dict(color=colours))])
    fig.update_layout(xaxis=dict(title='Track Attributes'), yaxis=dict(title='Value'), \
                      title=f'Song Attributes: {user_input}', showlegend=False, plot_bgcolor='#bfbdbd')

    fig.update_yaxes(range=[0, 1])
    return fig