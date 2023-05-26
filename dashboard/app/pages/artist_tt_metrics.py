from os import path
from dash import register_page, html, callback, dcc, Input, Output
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime

from helper_functions import get_db_connection

register_page(__name__, path="/artist_tiktok_metrics")


long_term_conn = get_db_connection(True)


def get_tt_artist_pop() -> list[dict]:
    '''
    Returns all artist in long term database that have a tiktok account and their metrics on tiktok
    '''
    sql_query = "select artist.artist_spotify_id, artist_tiktok_follower_count_in_hundred_thousands,\
          artist_tiktok_like_count_in_hundred_thousands, tiktok_artist_views.recorded_at as time, \
            artist.spotify_name from tiktok_artist_views join artist on artist.artist_spotify_id = \
                tiktok_artist_views.artist_spotify_id;"
    with long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_query)
        result = cur.fetchall()
    tt_artist_pop_df = pd.DataFrame(result)
    tt_artist_names = tt_artist_pop_df["spotify_name"]
    tt_artist_dates = tt_artist_pop_df.sort_values(by="time", ascending=True)
    pd.to_datetime(tt_artist_dates["time"])
    min_date = tt_artist_dates["time"].dt.date.min()
    max_date = tt_artist_dates["time"].dt.date.max() + timedelta(days=1)
    return tt_artist_pop_df, tt_artist_names, min_date, max_date




layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("Artist TikTok Metrics Over Time"),
    dcc.Dropdown(id="artist_names",
                 placeholder="Type in an artist name or select one\
                 from the dropdown"),
    dcc.Dropdown(options=["Follower count", "Likes"],
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
    while user_input_artist is None or user_input_metric is None or user_start_date is None or user_end_date is None:
        tt_artist_pop_df, tt_artist_names, min_date, max_date = get_tt_artist_pop()
        return px.line(), tt_artist_names, min_date, max_date
    if user_input_metric == "Follower count":
        metric = "artist_tiktok_follower_count_in_hundred_thousands"
    else:
        metric = "artist_tiktok_like_count_in_hundred_thousands"
    tt_artist_pop_df, tt_artist_names, min_date, max_date = get_tt_artist_pop()
    artist_df = tt_artist_pop_df[tt_artist_pop_df["spotify_name"]
                              == user_input_artist]
    artist_df = artist_df.loc[(artist_df["time"] <= (datetime.strptime(user_end_date, "%Y-%m-%d") + timedelta(days=1))) & (
        artist_df["time"] >= user_start_date)]
    fig = px.line(artist_df, x="time",
                  y=f"{metric}", title=f"{user_input_artist}'s {user_input_metric} over time")
    fig.update_yaxes(rangemode="tozero")
    return fig, tt_artist_names, min_date, max_date
