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

def get_all_current_songs(conn):
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "Select track.track_name, STRING_AGG(artist.spotify_name, ', ') AS artists FROM track \
            JOIN track_artist ON track.track_spotify_id = track_artist.track_spotify_id \
            JOIN artist ON track_artist.artist_spotify_id = artist.artist_spotify_id \
            GROUP BY track.track_name;"
        cur.execute(sql_query)
        result = cur.fetchall()
        # for item in result:
        #     print(item)
        #     print("   ")

get_all_current_songs(conn)

# Join name and artists together for output options (song - artists) (this is in the dropdown list, but as a type search)
# In graph function, split the name on " -", then use the first one to search the database for that song name
# Have empty graph (rather than error) for page without input (i.e. if user_input is None)