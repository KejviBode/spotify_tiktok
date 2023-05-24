from os import path
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

from helper_functions import conn

register_page(__name__, path="/artist_popularity")

def get_artist_pop():
    sql_query = "SELECT * FROM artist JOIN artist_popularity \
        ON artist.artist_spotify_id = artist_popularity.artist_spotify_id;"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql_query)
        result = cur.fetchall()
    return result

artist_pop = get_artist_pop()
artist_pop_df = pd.DataFrame(artist_pop)
artist_names = artist_pop_df["spotify_name"]
artist_dates = artist_pop_df["created_at"].sort_values(ascending=True)
MIN_DATE = artist_dates.dt.date.min()
MAX_DATE = artist_dates.dt.date.max()

layout = html.Main([
    html.Div(style={"margin-top": "100px"}),
    html.H1("Artist Popularity Over Time"),
    dcc.Dropdown(options=artist_names, 
                 id = "artist_names",
                 placeholder="Type in an artist name or select one\
                 from the dropdown!"),
    dcc.DatePickerRange(min_date_allowed=MIN_DATE,
                        max_date_allowed=MAX_DATE + timedelta(days=1),
                        id="date_slider",
                        display_format="D-M-Y"),
    # html.Div(id="text")
    dcc.Graph(id="popularity_graph")
])

@callback(
    Output(component_id="popularity_graph",
           component_property="figure"),
    # Output(component_id="text",component_property="children"),
    Input("artist_names", "value"), 
    [Input("date_slider", "start_date"),
     Input("date_slider", "end_date")]
)
def create_artist_popularity_graph(user_input_artist, user_start_date, user_end_date=MAX_DATE):
    print(user_input_artist)
    artist_df = artist_pop_df[artist_pop_df["spotify_name"] == user_input_artist]
    # artist_df_dates = artist_df.loc[(artist_df["created_at"] <= user_end_date) & (artist_df["created_at"]>=user_start_date)]
    # print(artist_df.columns)
    print(artist_df)
    return px.line(artist_df, y=artist_df["follower_count"], x=artist_df.loc[(artist_df["created_at"] <= user_end_date) & (artist_df["created_at"] >= user_start_date)]["created_at"])
