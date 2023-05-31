from os import path
from dash import register_page, html, callback, dcc, Input, Output
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime

from helper_functions import get_db_connection

register_page(__name__, path="/tiktok_track_metrics")


def get_track_names() -> list[str]:
    '''
    Returns a list of all track names
    '''
    long_term_conn = get_db_connection(True)
    sql_track_query = "SELECT track_name from track;"
    with long_term_conn, long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_track_query)
        result = cur.fetchall()
    track_names = []
    [track_names.append(track["track_name"]) for track in result]
    return track_names


def get_min_max_dates(track_name: str) -> str:
    '''
    Returns the min and max dates of when a track has entered the charts
    '''
    long_term_conn = get_db_connection(True)
    sql_date_query = "select min(DATE(tiktok_track_views.recorded_at)), max(DATE(tiktok_track_views.recorded_at)) \
                    FROM track JOIN tiktok_track_views ON track.track_spotify_id = tiktok_track_views.track_spotify_id\
                        WHERE track.track_name = %s;"
    with long_term_conn, long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_date_query, (track_name,))
        result = cur.fetchall()
    return result[0]["min"], result[0]["max"]


def get_tt_track_views(track_name: str) ->list[dict]:
    '''
    Returns track information 
    '''
    long_term_conn = get_db_connection(True)
    sql_query = "SELECT track.track_spotify_id, tiktok_track_views_in_hundred_thousands,\
          tiktok_track_views.recorded_at AS time, track.track_name FROM tiktok_track_views \
            JOIN track ON track.track_spotify_id = tiktok_track_views.track_spotify_id where track.track_name = %s\
                ORDER BY time ASC;"
    with long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_query, (track_name,))
        result = cur.fetchall()
    tt_track_views_df = pd.DataFrame(result)
    tt_track_names = tt_track_views_df["track_name"]
    tt_dates = tt_track_views_df.sort_values(by="time", ascending=True)
    pd.to_datetime(tt_dates["time"])
    min_date = tt_dates["time"].dt.date.min()
    max_date = tt_dates["time"].dt.date.max() + timedelta(days=1)
    return tt_track_views_df, tt_track_names, min_date, max_date


layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("TikTok Views Over Time"),
    dcc.Dropdown(id="tt_track_names",
                 placeholder="Type in a track name or select one\
                 from the dropdown"),
    dcc.DatePickerRange(id="track_date_slider",
                        display_format="D-M-Y"),
    dcc.Graph(id="views_graph")
])


@callback(
    Output(component_id="views_graph",
           component_property="figure"),
    Output(component_id="tt_track_names",
           component_property="options"),
    Output(component_id="track_date_slider",
           component_property="min_date_allowed"),
    Output(component_id="track_date_slider", 
           component_property="max_date_allowed"),
    Input("tt_track_names", "value"),
    [Input("track_date_slider", "start_date"),
     Input("track_date_slider", "end_date")]
)
def create_artist_popularity_graph(user_input_track, user_start_date, user_end_date):
    '''
    Creates a line graph showing an artist's popularity/follower count over time
    '''
    while user_input_track is None:
        tt_track_names = get_track_names()
        return px.line(), tt_track_names, datetime.now().date(), datetime.now().date()
    while user_start_date is None or user_end_date is None:
        tt_track_names = get_track_names()
        min_date, max_date = get_min_max_dates(user_input_track)
        return px.line(), tt_track_names, min_date, max_date
    tt_track_views_df, tt_track_names, min_date, max_date = get_tt_track_views(user_input_track)
    tt_track_names = get_track_names()
    track_df = tt_track_views_df[tt_track_views_df["track_name"]
                              == user_input_track]
    track_df = track_df.loc[(track_df["time"] <= (datetime.strptime(user_end_date, "%Y-%m-%d") + timedelta(days=1))) & (
        track_df["time"] >= user_start_date)]
    return px.line(track_df, x="time", y="tiktok_track_views_in_hundred_thousands", title=f"{user_input_track}'s TikTok views over time"), tt_track_names, min_date, max_date
