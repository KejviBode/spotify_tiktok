from os import path
from dash import register_page, html, callback, dcc, Input, Output
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime

from helper_functions import get_db_connection

register_page(__name__, path="/artist_popularity")


def get_artist_pop():
    long_term_conn = get_db_connection(True)
    sql_query = "SELECT * FROM artist JOIN artist_popularity on artist.artist_spotify_id = artist_popularity.artist_spotify_id;"
    with long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_query)
        result = cur.fetchall()
    artist_pop_df = pd.DataFrame(result)
    artist_names = artist_pop_df["spotify_name"]
    artist_dates = artist_pop_df.sort_values(by="created_at",ascending=True)
    pd.to_datetime(artist_dates["created_at"])
    min_date = artist_dates["created_at"].dt.date.min()
    max_date = artist_dates["created_at"].dt.date.max() + timedelta(days=1)
    return artist_pop_df, artist_names, min_date, max_date


layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("Artist Popularity Over Time"),
    dcc.Dropdown(id = "spotify_artist_names",
                 placeholder="Type in an artist name or select one\
                 from the dropdown"),
    dcc.Dropdown(options=["Follower count", "Popularity"],
                 id="follower_or_popularity",
                 placeholder="Please select how you'd like to track this artist"),
    dcc.DatePickerRange(id="pop_date_slider",
                        display_format="D-M-Y"),
    dcc.Graph(id="popularity_graph")
])


@callback(
    Output(component_id="popularity_graph",
           component_property="figure"),
    Output(component_id="spotify_artist_names",
           component_property="options"),
    Output(component_id="pop_date_slider",
           component_property="min_date_allowed"),
    Output(component_id="pop_date_slider",
           component_property="max_date_allowed"),
    Input("spotify_artist_names", "value"), 
    Input("follower_or_popularity", "value"),
    [Input("pop_date_slider", "start_date"),
     Input("pop_date_slider", "end_date")]
)
def create_artist_popularity_graph(user_input_artist, user_input_metric, user_start_date, user_end_date):
    '''
    Creates a line graph showing an artist's popularity/follower count over time
    '''
    while user_input_artist is None or user_input_metric is None or user_start_date is None or user_end_date is None:
        artist_pop_df, artist_names, min_date, max_date = get_artist_pop()
        return px.line(), artist_names, min_date, max_date
    if user_input_metric == "Follower count":
        metric = "follower_count"
    else:
        metric = "artist_popularity"
    artist_pop_df, artist_names, min_date, max_date = get_artist_pop()
    artist_df = artist_pop_df[artist_pop_df["spotify_name"] == user_input_artist]
    artist_df = artist_df.loc[(artist_df["created_at"] <= (datetime.strptime(user_end_date, "%Y-%m-%d")  + timedelta(days=1))) & (
        artist_df["created_at"] >= user_start_date)]
    return px.line(artist_df, x="created_at", y=f"{metric}", title=f"{user_input_artist}'s {user_input_metric} over time"), artist_names, min_date, max_date
