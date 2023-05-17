"""Hourly Lambda"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from spotify_api import get_db_connection, get_auth_token, get_auth_header, client_id, client_secret,\
    get_artist_followers, get_track_popularity, add_artist_popularity_data, add_track_popularity


def get_column_values(table_name: str, column_name: str) -> list[int]:
    """Takes a table and column name and returns a list of values from that table column"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = f"SELECT {column_name} FROM {table_name}"
        cur.execute(query)
        values = [row[f'{table_name}_spotify_id'] for row in cur.fetchall()]
    return values


def get_all_popularity(ids: list, headers: str, type: str) -> list[dict]:
    """Takes in a list of ids and returns a list of dicts with popularity data"""
    popularity_scores = []
    for id in ids:
        popularity_data = {"id": id}
        if type == "track":
            popularity_data["popularity"] = get_track_popularity(id, headers)
        elif type == "artist":
            track_popularity = get_artist_followers(id, headers)
            popularity_data["popularity"] = track_popularity["popularity"]
            popularity_data["follower_count"] = track_popularity["follower_count"]
        popularity_scores.append(popularity_data)
    return popularity_scores
        

def add_popularity_to_database(popularity_data: list[dict], type: str, conn):
    """Takes in a list of dicts of popularity data and enters them into the database"""
    for item in popularity_data:
        if type == "track":
            add_track_popularity(item["id"], item["popularity"], conn)
        elif type == "artist":
            add_artist_popularity_data(item["id"], item["popularity"], item["follower_count"], conn)



if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    tracks = get_column_values("track", "track_spotify_id")
    artists = get_column_values("artist", "artist_spotify_id")

    token = get_auth_token(client_id, client_secret)
    print("Connected to API")

    headers = get_auth_header(token)

    track_popularity = get_all_popularity(tracks, headers, "track")
    print("Collected track popularity")
    artist_popularity = get_all_popularity(artists, headers, "artist")
    print("Collected artist popularity")

    add_popularity_to_database(track_popularity, "track", conn)
    print("Added track data to database")
    add_popularity_to_database(artist_popularity, "artist", conn)
    print("Added artist data to database")