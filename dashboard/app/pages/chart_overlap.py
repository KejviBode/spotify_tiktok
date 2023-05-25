from os import path
from datetime import date, timedelta
from dash import Dash, register_page, html, page_container, callback, dcc, Input, Output, dash_table
import psycopg2
import plotly.express as px
from psycopg2.extras import RealDictCursor


from helper_functions import conn, long_conn

register_page(__name__, path="/chart_overlap")

layout = html.Main([html.Div(style={"margin-top": "100px"}),
    html.H1("Chart Overlap", style={'color': 'Black'}),
                    dcc.Dropdown(["None", "1 Day", "2 Days", "3 Days", "5 Days", "7 Days"], id="pie-dropdown", placeholder="Choose No. Days Lag"),
                    html.Div(dcc.Graph(id="pie-graph", style={'height': '700px', 'width': '700px'}),
                             style={"display": "flex", "justify-content": "center", "align-items": "center", "height": "700px"})])

@callback(Output(component_id="pie-graph", component_property="figure"),
          Input("pie-dropdown", "value"))
def pie_chart(user_input):
    '''
    Creates a pie chart of the songs in the Spotify chart, TikTok chart, and both charts
    '''
    if user_input == "None" or user_input == None:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql_query = 'SELECT \
                COUNT(*) AS count_spotify_only, \
                (SELECT COUNT(*) FROM track WHERE in_tiktok = TRUE AND in_spotify = FALSE) AS count_tiktok_only, \
                (SELECT COUNT(*) FROM track WHERE in_tiktok = TRUE AND in_spotify = TRUE) AS count_both \
                FROM track \
                WHERE in_spotify = TRUE AND in_tiktok = FALSE;'
            cur.execute(sql_query)
            result = cur.fetchone()
        spotify_only_count = result["count_spotify_only"]
        tiktok_only_count = result["count_tiktok_only"]
        both_count = result["count_both"]
    
    else:
        today = date.today()
        lag = today - timedelta(days=int(user_input.split()[0]))
        with long_conn, long_conn.cursor() as cur:
            sql_query2 = "SELECT track_spotify_id from track WHERE DATE_TRUNC('day', recorded_at) = DATE %s AND in_tiktok = True;"
            vals = (lag,)
            cur.execute(sql_query2, vals)
            results = cur.fetchall()
            if len(results) == 0:
                fig = px.pie(title="No Data Available")
                fig.update_layout(title={"text": fig["layout"]["title"]["text"], "x": 0.5})
                return fig
            result_list = []
            for item in results:
                result_list.append(item[0])
        tiktok_only_count = 0
        both_count = 0
        for item in results:
            with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql_query3 = "SELECT COUNT(*) from track WHERE track_spotify_id = %s AND in_spotify = True;"
                vals = (item[0],)
                cur.execute(sql_query3, vals)
                result = cur.fetchone()
                if result["count"] == 1:
                    both_count += 1
                if result["count"] == 0:
                    tiktok_only_count += 1
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql_query3 = "Select COUNT(*) from track WHERE in_spotify = True;"
            cur.execute(sql_query3)
            in_spotify_count = cur.fetchone()
            spotify_only_count = in_spotify_count["count"] - both_count
    

    data = {
            'Platforms': ['Spotify Only', 'TikTok Only', 'Both'],
            'Count': [spotify_only_count, tiktok_only_count, both_count]
        }
    colours = ['#ff0050', '#1ed760', '#00f2ea',]

    fig = px.pie(data, values='Count', names='Platforms', title='Platform Distribution', color_discrete_sequence=colours)
    fig.update_layout(title={"text": fig["layout"]["title"]["text"], "x": 0.465})
    return fig