import os
from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import date, timedelta, datetime

from helper_functions import get_db_connection, get_all_current_songs

register_page(__name__, path="/chart_position")


long_conn = get_db_connection(True)

songs = get_all_current_songs(long_conn)

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Chart Position", style={'color': 'Black'}),
                    dcc.Dropdown(options=[{'label': song, 'value': song} for song in songs], id="chart-dropdown", placeholder="Choose One"),
                    dcc.Graph(id="chart-graph")])


@callback(Output(component_id="chart-graph", component_property="figure"),
          Input("chart-dropdown", "value"))
def get_song_chart_positions(user_input):
    '''
    Gets chart position by date for given song
    '''
    if user_input is None:
        return px.line()
    song_name = user_input
    last_dash_index = user_input.rfind("-")
    song_name = user_input[:last_dash_index].strip()
    with long_conn, long_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "Select tiktok_rank, spotify_rank, recorded_at FROM track WHERE track_name = %s"
        vals = (song_name,)
        cur.execute(sql_query, vals)
        results = cur.fetchall()
    
    chart_data = pd.DataFrame(columns=['tiktok_rank', 'spotify_rank', 'recorded_at'])
    for item in results:
        new_row = [item["tiktok_rank"], item["spotify_rank"], item["recorded_at"].date()]
        chart_data.loc[len(chart_data)] = new_row
    chart_data['tiktok_rank'] = pd.to_numeric(chart_data['tiktok_rank'])
    chart_data['spotify_rank'] = pd.to_numeric(chart_data['spotify_rank'])
    chart_data['recorded_at'] = pd.to_datetime(chart_data['recorded_at'])
    
    chart_data_sorted = chart_data.sort_values('recorded_at')
    fig = px.line(chart_data_sorted, x='recorded_at', y=['tiktok_rank', 'spotify_rank'], 
              title='Change in Chart Position',
              labels={'value': 'Rank', 'recorded_at': 'Date'},
              line_group='variable', color='variable')
    return fig