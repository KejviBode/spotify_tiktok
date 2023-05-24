from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd

def get_db_connection(long_term: bool=False):
    """Connects to the database"""
    if long_term == True:
        db_name = "DB_LONG_TERM_NAME"
        db_host = "DB_LONG_TERM_HOST"
    else:
        db_name = "DB_NAME"
        db_host = "DB_HOST"
    try:
        conn = psycopg2.connect(
            user=os.environ["DB_USER"],
            host=os.environ[db_host],
            database=os.environ[db_name],
            password=os.environ['DB_PASSWORD'],
            port=os.environ['DB_PORT']
        )
        return conn
    except Exception as err:
        print(err)
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
long_conn = get_db_connection(True)

def get_all_current_songs(conn):
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "Select track.track_name, STRING_AGG(artist.spotify_name, ', ') AS artists FROM track \
            JOIN track_artist ON track.track_spotify_id = track_artist.track_spotify_id \
            JOIN artist ON track_artist.artist_spotify_id = artist.artist_spotify_id \
            GROUP BY track.track_name;"
        cur.execute(sql_query)
        result = cur.fetchall()
        result_list = []
        for item in result:
            result_list.append(f"{item['track_name']} - {item['artists']}")
    return result_list


