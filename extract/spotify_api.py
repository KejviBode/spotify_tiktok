"""Daily Lambda"""

import base64
import json
import os
from dotenv import load_dotenv
from requests import post, get
import psycopg2
from psycopg2.extras import RealDictCursor


BUCKET_NAME = "c7-spotify-tiktok-output"
SPOTIFY_BASE_URL = "http://api.spotify.com/v1/"
TOP_50_PLAYLIST_ID = "37i9dQZEVXbMDoHDwVN2tF"
TRACK_FILENAME = 'track_ids.csv'
ARTIST_FILENAME = 'artist_ids.csv'


def get_auth_token(client_id: str, client_secret: str) -> str:
    """Gets an authorisation token from Spotify API"""
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data, timeout=10)
    json_result = json.loads(result.content)
    return json_result["access_token"]


def get_auth_header(token: str) -> dict:
    """Takes in authorisation token and returns header for API calls"""
    return {"Authorization": "Bearer " + token}


def get_spotify_top_50(top_50_uri: str, headers: dict) -> list[dict]:
    """Takes playlist id and returns list of dictionaries of tracks in the playlist"""
    result = get(f"{SPOTIFY_BASE_URL}playlists/{top_50_uri}/tracks", headers=headers, timeout=10)
    result = json.loads(result.content)
    return result["items"]


def create_track_dicts(items: list[dict]) -> list[dict]:
    """Takes in a list of playlist items and returns a list of dictionaries of each track"""
    tracks = []
    rank = 0
    for item in items:
        rank += 1
        track = {}
        track["id"] = item["track"]["id"]
        track["name"] = item["track"]["name"]
        track["spotify_rank"] = rank
        track["tiktok_rank"] = None
        track["in_spotify"] = True
        track["in_tiktok"] = False
        track["popularity"] = get_track_popularity(track["id"], headers)
        audio_features = get_track_audio_features(track["id"], headers)
        track["danceability"] = audio_features["danceability"]
        track["energy"] = audio_features["energy"]
        track["valence"] = audio_features["valence"]
        track["tempo"] = audio_features["tempo"]
        track["speechiness"] = audio_features["speechiness"]

        track["artists"] = []
        for artist in item["track"]["artists"]:
            artist_dict = {}
            artist_dict["id"] = artist["id"]
            artist_dict["name"] = artist["name"]
            artist_followers = get_artist_followers(artist["id"], headers)
            artist_dict["popularity"] = artist_followers["popularity"]
            artist_dict["follower_count"] = artist_followers["follower_count"]
            artist_dict["genres"] = artist_followers["genres"]
            track["artists"].append(artist_dict)
        tracks.append(track)
    return tracks


def get_artist_followers(artist_id: str, headers: dict) -> dict:
    """Takes an artist id and gets the popularity rating and follower count for that artist"""
    result = get(f"{SPOTIFY_BASE_URL}artists/{artist_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    artist_followers = {}
    artist_followers["popularity"] = result["popularity"]
    artist_followers["follower_count"] = result["followers"]["total"]
    artist_followers["genres"] = result["genres"]
    return artist_followers


def get_track_popularity(track_id: str, headers: dict) -> str:
    """Takes a track id and gets the popularity rating of that track"""
    result = get(f"{SPOTIFY_BASE_URL}tracks/{track_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    if "popularity" in result:
        popularity = result["popularity"]
    else:
        popularity = None
    return popularity


def get_track_audio_features(track_id: str, headers: dict) -> dict:
    """Takes a track id and gets danceability, energy, valence, tempo, and speechiness scores"""
    result = get(f"{SPOTIFY_BASE_URL}audio-features/{track_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    audio_features = {}
    audio_features["danceability"] = result["danceability"]
    audio_features["energy"] = result["energy"]
    audio_features["valence"] = result["valence"]
    audio_features["tempo"] = result["tempo"]
    audio_features["speechiness"] = result["speechiness"]
    return audio_features


def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            database = os.getenv("DB")
            )
        print("Connected")
        return conn
    except Exception as e:
        print(e)
        print("Error connecting to database.")


def add_track_data(data: list[dict]) -> list[dict]:
    """Takes in data on tracks and inserts track details into the track table"""
    for track in data:
        with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql_input = "INSERT INTO track (track_name, track_danceability, track_energy, \
                track_valence, track_tempo, track_speechiness, in_spotify, in_tiktok, \
                    tiktok_rank, spotify_rank, track_spotify_id)\
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
            vals = [track["name"], track["danceability"], track["energy"], track["valence"], \
                    track["tempo"], track["speechiness"], track["in_spotify"], \
                    track["in_tiktok"], track["tiktok_rank"], \
                    track["spotify_rank"], track["id"]]
            cur.execute(sql_input, vals)
            conn.commit()
        add_track_popularity(track["id"], track["popularity"], conn)
    return data


def add_artist_data(data: list):
    """Takes in data on tracks and inserts artist details into the artist table"""
    for track in data:
        for artist in track["artists"]:
            with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql_input = "INSERT INTO artist (spotify_name, artist_spotify_id)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
                vals = [artist["name"], artist["id"]]
                cur.execute(sql_input, vals)
                conn.commit()
            add_artist_popularity_data(artist["id"], artist["popularity"], artist["follower_count"], conn)
            for genre in artist["genres"]:
                genre_id = add_genre(genre)
                add_artist_genre(genre_id, artist["id"])
            add_track_artist(track["id"], artist["id"])
    return data


def add_artist_popularity_data(artist_id: str, popularity: int, follower_count: int, conn):
    """Takes in data on artist popularity and enters into the artist_popularity table"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO artist_popularity (artist_spotify_id, artist_popularity, \
            follower_count)\
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [artist_id, popularity, follower_count]
        cur.execute(sql_input, vals)
        conn.commit()


def add_genre(genre_name: str) -> int:
    """Takes in a genre name, adds to the database if not there, and returns genre id"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("INSERT INTO genre (genre_name) VALUES (%s) \
                        ON CONFLICT DO NOTHING", (genre_name,))
        conn.commit()
        cur.execute("SELECT genre_id FROM genre WHERE genre_name = %s", (genre_name,))
        genre_id = cur.fetchone()
    return genre_id['genre_id']


def add_artist_genre(genre_id: int, artist_id: int):
    """Takes in a genre id and artist id and adds them to the artist_genre table"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO artist_genre (genre_id, artist_spotify_id)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [genre_id, artist_id]
        cur.execute(sql_input, vals)
        conn.commit()


def add_track_popularity(track_id: int, popularity: int, conn):
    """Takes in a track id and popularity and adds them to the track_popularity table"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO track_popularity (track_spotify_id, popularity_score)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [track_id, popularity]
        cur.execute(sql_input, vals)
        conn.commit()


def add_track_artist(track_id: int, artist_id: int):
    """Takes in a track id and artist id and adds them to the track_artist table"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO track_artist (track_spotify_id, artist_spotify_id)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [track_id, artist_id]
        cur.execute(sql_input, vals)
        conn.commit()


if __name__ == "__main__":
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    token = get_auth_token(client_id, client_secret)
    print("Connected to API")

    headers = get_auth_header(token)
    result = get_spotify_top_50(TOP_50_PLAYLIST_ID, headers)
    tracks = create_track_dicts(result)
    print("Gathered top 50")

    conn = get_db_connection()
    data_with_id = add_track_data(tracks)
    print("Added tracks")
    data_with_artist_id = add_artist_data(data_with_id)
    print("Added artists")
    print("Success!")
