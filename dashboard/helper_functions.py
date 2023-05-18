from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor

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
            'track_name': row[0],
            'spotify_rank': row[1] if row[1] is not None else 'N/A',
            'tiktok_rank': row[2] if row[1] is not None else 'N/A',
            'spotify_names': ', '.join(row[3]) if row[3] else '',
        }
        top_entries.append(track_dict)

    return top_entries



load_dotenv()
conn = get_db_connection()

