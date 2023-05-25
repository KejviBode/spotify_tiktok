import os
from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import date, timedelta, datetime

from helper_functions import get_db_connection, get_all_current_songs

# register_page(__name__, path="/chart_position")


long_term_conn = get_db_connection(True)

songs = get_all_current_songs(long_conn)

# def get_artist_pop():
#     sql_query = "SELECT * FROM artist JOIN artist_popularity on artist.artist_spotify_id = artist_popularity.artist_spotify_id;"
#     with long_term_conn.cursor(cursor_factory=RealDictCursor) as cur:
#         cur.execute(sql_query)
#         result = cur.fetchall()
#     return result

# artist_pop = get_artist_pop()
# artist_pop_df = pd.DataFrame(artist_pop)
# artist_names = artist_pop_df["spotify_name"]
# artist_dates = artist_pop_df.sort_values(by="created_at",ascending=True)
# pd.to_datetime(artist_dates["created_at"])
# MIN_DATE = artist_dates["created_at"].dt.date.min()
# MAX_DATE = artist_dates["created_at"].dt.date.max()



# layout = html.Main([
#     html.Div(style={"margin-top": "100px"}),
#     html.H1("Artist Popularity Over Time"),
#     dcc.Dropdown(options=artist_names, 
#                  id = "artist_names",
#                  placeholder="Type in an artist name or select one\
#                  from the dropdown"),
#     dcc.DatePickerRange(min_date_allowed=MIN_DATE,
#                         max_date_allowed=MAX_DATE + timedelta(days=1),
#                         id="date_slider",
#                         display_format="D-M-Y"),
#     dcc.Graph(id="popularity_graph")
# ])

# @callback(
#     Output(component_id="popularity_graph",
#            component_property="figure"),
#     Input("artist_names", "value"), 
#     [Input("date_slider", "start_date"),
#      Input("date_slider", "end_date")]
# )
# def create_artist_popularity_graph(user_input_artist, user_start_date, user_end_date=MAX_DATE):
#     while user_input_artist is None or user_start_date is None or user_end_date is None:
#         return px.line()
#     artist_df = artist_pop_df[artist_pop_df["spotify_name"] == user_input_artist]
#     artist_df = artist_df.loc[(artist_df["created_at"] <= (datetime.strptime(user_end_date, "%Y-%m-%d")  + timedelta(days=1))) & (
#         artist_df["created_at"] >= user_start_date)]
#     # artist_df_dates = artist_df.loc[(artist_df["created_at"] <= user_end_date) & (artist_df["created_at"]>=user_start_date)]
#     # print(artist_df.columns)
#     # print(artist_df)
#     return px.line(artist_df, x="created_at", y="follower_count", title=f"{user_input_artist}'s popularity over time")
