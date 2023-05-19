from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd

def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            database = os.getenv("DB_NAME")
            )
        print("Connected")
        return conn
    except Exception as e:
        print(e)
        print("Error connecting to database.")


def get_top_ten(chart_type: str, conn) -> list[dict]:
    """Finds top 10 entries for Spotify or TikTok and returns a list of dicts"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT t.track_name, t.spotify_rank, t.tiktok_rank, ARRAY_AGG(a.spotify_name) AS spotify_names
            FROM track AS t
            INNER JOIN track_artist AS ta ON t.track_spotify_id = ta.track_spotify_id
            INNER JOIN artist AS a ON ta.artist_spotify_id = a.artist_spotify_id
            WHERE t.{chart_type}_rank BETWEEN 1 AND 10
            GROUP BY t.track_name, t.spotify_rank, t.tiktok_rank
            ORDER BY t.{chart_type}_rank
        """)
        rows = cur.fetchall()

    top_entries = []
    for row in rows:
        track_dict = {
            'track_name': row["track_name"],
            'spotify_rank': row['spotify_rank'] if row['spotify_rank'] is not None else 'N/A',
            'tiktok_rank': row['tiktok_rank'] if row['tiktok_rank'] is not None else 'N/A',
            'spotify_names': ', '.join(row['spotify_names']) if row['spotify_names'] else '',
        }
        top_entries.append(track_dict)

    return top_entries



load_dotenv()
conn = get_db_connection()

def attribute_bar_chart(user_input):
    # if user_input == "All":
    #     return "All"
    # elif user_input == "Spotify":
    #     return "Spotify"
    with conn, conn.cursor() as cur:
        sql_input = '''
            SELECT
                CASE
                    WHEN in_spotify IS TRUE AND in_tiktok IS TRUE THEN 'In TikTok Charts'
                    WHEN in_spotify IS TRUE AND in_tiktok IS FALSE THEN 'Not in TikTok Charts'
                END AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_speechiness) AS avg_speechiness
            FROM
                track
            GROUP BY
                situation
        '''
        cur.execute(sql_input)
        results = cur.fetchall()
        print(results)

    # situations = [result[0] for result in results]
    # attributes = ['Danceability', 'Energy', 'Valence', 'Speechiness']
    # averages = [[result[i] for result in results] for i in range(1, 6)]

    # fig = px.bar(x=situations, y=averages, barmode='group', labels={'x': 'Situation', 'y': 'Average Value'}, title='Average Qualities by Situation')
    # fig = fig.update_layout(xaxis=dict(tickmode='array', tickvals=list(range(len(attributes))), ticktext=attributes), yaxis=dict(title='Average Value'))
    # return fig
    # else:
    #     return "TikTok"
    situations = [item[0] for item in results]
    danceability = [item[1] for item in results]
    energy = [item[2] for item in results]
    valence = [item[3] for item in results]
    speechiness = [item[4] for item in results]

    fig = px.bar(
        x=situations,
        y=[danceability, energy, valence, speechiness],
        barmode='group',
        labels={'x': 'Situation', 'y': 'Value'},
        title='Bar Chart with Two Groups'
    )

    fig.update_layout(
        xaxis=dict(title='Situation'),
        yaxis=dict(title='Value'),
        legend=dict(title='Attributes')
        ticktext=attributes,
        tickvals=list(range(len(attributes)))
    )

    fig.show()

attribute_bar_chart("x")