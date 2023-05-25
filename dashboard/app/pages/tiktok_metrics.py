from os import path
from dash import register_page, html, callback, dcc, Input, Output
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime

from helper_functions import get_db_connection

register_page(__name__, path="/tiktok_track_metrics")


long_term_conn = get_db_connection(True)


def get_tt_track_views() ->list[dict]:
    '''
    Returns track information 
    '''
    sql_query = "SELECT track.track_spotify_id, tiktok_track_views_in_hundred_thousands,\
          tiktok_track_views.recorded_at AS time, track.track_name FROM tiktok_track_views \
            JOIN track ON track.track_spotify_id = tiktok_track_views.track_spotify_id;"
    with long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_query)
        result = cur.fetchall()
    return result


tt_track_views = get_tt_track_views()
tt_track_views_df = pd.DataFrame(tt_track_views)
tt_track_names = tt_track_views_df["track_name"]
tt_dates = tt_track_views_df.sort_values(by="time", ascending=True)
pd.to_datetime(tt_dates["time"])
MIN_DATE = tt_dates["time"].dt.date.min()
MAX_DATE = tt_dates["time"].dt.date.max() + timedelta(days=1)


layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("TikTok Views Over Time"),
    dcc.Dropdown(options=tt_track_names,
                 id="tt_track_names",
                 placeholder="Type in an artist name or select one\
                 from the dropdown"),
    dcc.DatePickerRange(min_date_allowed=MIN_DATE,
                        max_date_allowed=MAX_DATE,
                        id="date_slider",
                        display_format="D-M-Y"),
    dcc.Graph(id="views_graph")
])


@callback(
    Output(component_id="views_graph",
           component_property="figure"),
    Input("tt_track_names", "value"),
    [Input("date_slider", "start_date"),
     Input("date_slider", "end_date")]
)
def create_artist_popularity_graph(user_input_track, user_start_date, user_end_date=MAX_DATE):
    '''
    Creates a line graph showing an artist's popularity/follower count over time
    '''
    while user_input_track is None or user_start_date is None or user_end_date is None:
        return px.line()
    track_df = tt_track_views_df[tt_track_views_df["track_name"]
                              == user_input_track]
    track_df = track_df.loc[(track_df["time"] <= (datetime.strptime(user_end_date, "%Y-%m-%d") + timedelta(days=1))) & (
        track_df["time"] >= user_start_date)]
    return px.line(track_df, x="time", y="tiktok_track_views_in_hundred_thousands", title=f"{user_input_track}'s TikTok views over time")
