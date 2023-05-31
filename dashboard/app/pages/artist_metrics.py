from os import path
from dash import register_page, html, callback, dcc, Input, Output
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime

from helper_functions import get_db_connection
from pandas import DataFrame

register_page(__name__, path="/artist_tiktok_metrics")

def get_tt_artist_names() -> list[str]:
    '''
    Returns a list of all artist names in the long term database
    '''
    long_term_conn = get_db_connection(True)
    sql_name_query = "select spotify_name from artist;"
    with long_term_conn, long_term_conn.cursor() as cur:
        cur.execute(sql_name_query)
        result = cur.fetchall()
    names = []
    [names.extend(name) for name in result]
    return names


def get_min_max_dates(artist_name: str) -> str:
    '''
    Returns the min and max dates of when artist has entered the charts
    '''
    long_term_conn = get_db_connection(True)
    sql_date_query = "select min(DATE(tiktok_artist_views.recorded_at)), max(DATE(tiktok_artist_views.recorded_at)) \
        FROM artist JOIN tiktok_artist_views ON artist.artist_spotify_id = tiktok_artist_views.artist_spotify_id\
              WHERE artist.spotify_name = %s"
    with long_term_conn, long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_date_query, (artist_name,))
        result = cur.fetchall()
    return result[0]["min"], result[0]["max"]


def get_artist_spotify_pop(long_term_conn, name: str = None) -> DataFrame:
    '''
    Returns a dataframe, artist names, a min date and a max date when the specified artist entered the charts
    '''
    long_term_conn = get_db_connection(True)
    sql_query = "SELECT *, created_at AS time FROM artist JOIN artist_popularity on artist.artist_spotify_id = \
        artist_popularity.artist_spotify_id WHERE artist.spotify_name = %s ORDER BY time ASC;"
    with long_term_conn, long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_query, (name,))
        result = cur.fetchall()
    artist_pop_df = pd.DataFrame(result)
    artist_names = artist_pop_df["spotify_name"]
    artist_dates = artist_pop_df.sort_values(by="created_at", ascending=True)
    pd.to_datetime(artist_dates["created_at"])
    min_date = artist_dates["created_at"].dt.date.min()
    max_date = artist_dates["created_at"].dt.date.max() + timedelta(days=1)
    return artist_pop_df, artist_names, min_date, max_date


def get_tt_artist_pop(metric: str, name: str = None) -> list[dict]:
    '''
    Returns all artist in long term database that have a tiktok account and their metrics on tiktok
    '''
    long_term_conn = get_db_connection(True)
    if name is None:
        sql_query = "select artist.artist_spotify_id, artist_tiktok_follower_count_in_hundred_thousands,\
            artist_tiktok_like_count_in_hundred_thousands, tiktok_artist_views.recorded_at as time, \
                artist.spotify_name from tiktok_artist_views join artist on artist.artist_spotify_id = \
                    tiktok_artist_views.artist_spotify_id ORDER BY time ASC;"
        with long_term_conn, long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_query)
            result = cur.fetchall()
    elif name is not None and metric in ["TikTok follower count", "TikTok likes"]:
        sql_query = "select artist.artist_spotify_id, artist_tiktok_follower_count_in_hundred_thousands,\
                    artist_tiktok_like_count_in_hundred_thousands, tiktok_artist_views.recorded_at as time, \
                    artist.spotify_name from tiktok_artist_views join artist on artist.artist_spotify_id = \
                    tiktok_artist_views.artist_spotify_id where spotify_name = %s ORDER BY time ASC;"
        with long_term_conn, long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_query, (name,))
            result = cur.fetchall()
    elif name is not None and metric in ["Spotify follower count", "Spotify popularity"]:
        return get_artist_spotify_pop(long_term_conn, name)
    tt_artist_pop_df = pd.DataFrame(result)
    tt_artist_names = tt_artist_pop_df["spotify_name"]
    pd.to_datetime(tt_artist_pop_df["time"])
    tt_artist_dates = tt_artist_pop_df.sort_values(by="time", ascending=True)
    min_date = tt_artist_dates["time"].dt.date.min()
    max_date = tt_artist_dates["time"].dt.date.max() + timedelta(days=1)
    return tt_artist_pop_df, tt_artist_names, min_date, max_date


layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("Artist Metrics Over Time"),
    dcc.Dropdown(id="artist_names",
                 placeholder="Type in an artist name or select one\
                 from the dropdown"),
    dcc.Dropdown(options=["TikTok follower count", "TikTok likes", "Spotify follower count", "Spotify popularity"],
                 id="follower_or_likes",
                 placeholder="Please select how you'd like to track this artist"),
    dcc.DatePickerRange(id="date_slider",
                        display_format="D-M-Y"),
    dcc.Graph(id="follower_graph")
])


@callback(
    Output(component_id="follower_graph",
           component_property="figure"),
    Output(component_id="artist_names",
           component_property="options"),
    Output(component_id="date_slider",
           component_property="min_date_allowed"),
    Output(component_id="date_slider", 
           component_property="max_date_allowed"),
    Input("artist_names", "value"),
    Input("follower_or_likes", "value"),
    [Input("date_slider", "start_date"),
     Input("date_slider", "end_date")]
)
def create_artist_popularity_graph(user_input_artist, user_input_metric, user_start_date, user_end_date):
    '''
    Creates a line graph showing an artist's popularity/follower count over time
    '''
    while user_input_artist is None:
        # tt_artist_pop_df, tt_artist_names, min_date, max_date = get_tt_artist_pop()
        tt_artist_names = get_tt_artist_names()
        return px.line(), tt_artist_names, datetime.now().date(), datetime.now().date()
    while user_input_metric is None or user_start_date is None or user_end_date is None:
        tt_artist_names = get_tt_artist_names()
        min_date, max_date = get_min_max_dates(user_input_artist)
        return px.line(), tt_artist_names, min_date, max_date
    if user_input_metric == "TikTok follower count":
        metric = "artist_tiktok_follower_count_in_hundred_thousands"
    elif user_input_metric == "TikTok likes":
        metric = "artist_tiktok_like_count_in_hundred_thousands"
    elif user_input_metric == "Spotify follower count":
        metric = "follower_count"
    else:
        metric = "artist_popularity"
    tt_artist_pop_df, tt_artist_names, min_date, max_date = get_tt_artist_pop(user_input_metric, user_input_artist)
    complete_tt_artist_names = get_tt_artist_names()
    artist_df = tt_artist_pop_df[tt_artist_pop_df["spotify_name"]
                              == user_input_artist]
    artist_df = artist_df.loc[(artist_df["time"] <= (datetime.strptime(user_end_date, "%Y-%m-%d") + timedelta(days=1))) & (
        artist_df["time"] >= user_start_date)]
    fig = px.line(artist_df, x="time",
                  y=f"{metric}", title=f"{user_input_artist}'s {user_input_metric} over time")
    # fig.update_yaxes(rangemode="tozero")
    return fig, complete_tt_artist_names, min_date, max_date
