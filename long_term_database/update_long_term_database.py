import os
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv


def get_db_connection(long_term: bool):
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


def load_track_data(short_conn: connection, long_conn: connection):
    """Loads data into track table in long term database"""
    with short_conn, short_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT * FROM track;"
        cur.execute(sql_query)
        result = cur.fetchall()

    with long_conn, long_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "INSERT INTO track (track_spotify_id, track_name, track_danceability, \
            track_energy, track_valence, track_tempo, track_speechiness, in_spotify, \
                in_tiktok, tiktok_rank, spotify_rank, recorded_at) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [(track["track_spotify_id"], track["track_name"], track["track_danceability"], \
                    track["track_energy"], track["track_valence"], track["tempo"], track["speechiness"], \
                    track["in_spotify"], track["in_tiktok"], track["tiktok_rank"], track["spotify_rank"], \
                    track["created_at"]) for track in result]
        execute_values(cur, sql_query, vals)
        long_conn.commit()


def load_artist_data(short_conn: connection, long_conn: connection):
    """Loads data into artist table in long term database"""
    with short_conn, short_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT artist.artist_spotify_id, artist.spotify_name, STRING_AGG(genre.genre_name, ', ') AS genre_names \
            FROM artist \
            JOIN artist_genre ON artist.artist_spotify_id = artist_genre.artist_spotify_id \
            JOIN genre ON artist_genre.genre_id = genre.genre_id \
            GROUP BY artist.artist_spotify_id, artist.spotify_name;"
        cur.execute(sql_query)
        result = cur.fetchall()

    with long_conn, long_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "INSERT INTO artist (artist_spotify_id, spotify_name, artist_genres) \
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [(artist["artist_spotify_id"], artist["spotify_name"], artist["artist_genres"]) \
                    for artist in result]
        execute_values(cur, sql_query, vals)
        long_conn.commit()


def load_track_artist_data(short_conn: connection, long_conn: connection):
    """Loads data into track_artist table in long term database"""
    with short_conn, short_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT * from track_artist;"
        cur.execute(sql_query)
        result = cur.fetchall()

    with long_conn, long_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "INSERT INTO track_artist (track_spotify_id, artist_spotify_id) \
                    SELECT %s, %s \
                    WHERE NOT EXISTS ( \
                        SELECT 1 \
                        FROM track_artist \
                        WHERE track_spotify_id = %s AND artist_spotify_id = %s) \
                    ON CONFLICT DO NOTHING"

        vals = [(item["track_spotify_id"], item["artist_spotify_id"], item["track_spotify_id"], \
                item["artist_spotify_id"]) for item in result]
        execute_values(cur, sql_query, vals)
        long_conn.commit()


def load_track_popularity_data(short_conn: connection, long_conn: connection):
    """Loads data into track_popularity table in long term database"""
    with short_conn, short_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT * from track_popularity;"
        cur.execute(sql_query)
        result = cur.fetchall()

    with long_conn, long_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "INSERT INTO track_popularity (track_spotify_id, popularity_score, created_at) \
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [(item["track_spotify_id"], item["popularity_score"], item["created_at"]) \
                for item in result]
        execute_values(cur, sql_query, vals)
        long_conn.commit()


def load_artist_popularity_data(short_conn: connection, long_conn: connection):
    """Loads data into artist_popularity table in long term database"""
    with short_conn, short_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT * from artist_popularity;"
        cur.execute(sql_query)
        result = cur.fetchall()

    with long_conn, long_conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "INSERT INTO artist_popularity (artist_spotify_id, artist_popularity, \
                      follower_count, created_at) \
                    VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [(item["artist_spotify_id"], item["artist_popularity"], item["follower_count"], \
                 item["created_at"]) for item in result]
        execute_values(cur, sql_query, vals)
        long_conn.commit()


def empty_short_term_tables(short_conn: connection):
    """Removes all the short term data from the database"""
    tables = ["track_popularity", "artist_popularity", "artist_genre", "track_artist", \
              "genre", "track", "artist"]
    with short_conn, short_conn.cursor(cursor_factory=RealDictCursor) as cur:
        for table in tables:
            cur.execute("DELETE FROM %s;", (table,))
            short_conn.commit()


if __name__ == "__main__":
    load_dotenv()
    short_conn = get_db_connection(False)
    long_conn = get_db_connection(True)
    load_track_data(short_conn, long_conn)
    load_artist_data(short_conn, long_conn)
    load_track_artist_data(short_conn, long_conn)
    load_track_popularity_data(short_conn, long_conn)
    load_artist_popularity_data(short_conn, long_conn)
    empty_short_term_tables(short_conn)
