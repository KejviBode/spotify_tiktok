import base64
import json
import os
from requests import post, get
import psycopg2
from psycopg2.extras import RealDictCursor

SPOTIFY_BASE_URL = "http://api.spotify.com/v1/"

def get_auth_token(client_id: str, client_secret: str) -> str:
    '''
    Gets an authorisation token from Spotify API
    '''
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
    '''
    Takes in authorisation token and returns header for API calls
    '''
    return {"Authorization": "Bearer " + token}


def get_db_connection():
    '''
    Connects to the database
    '''
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


def get_track_popularity(track_id: str, headers: dict) -> tuple:
    '''
    Takes a track id and gets the popularity rating of that track
    '''
    result = get(f"{SPOTIFY_BASE_URL}tracks/{track_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    if "popularity" in result:
        popularity = result["popularity"]
    else:
        popularity = None
    return popularity


def get_artist_followers(artist_id: str, headers: dict) ->tuple:
    '''
    Takes an artist id and gets the popularity rating and follower count for that artist
    '''
    result = get(f"{SPOTIFY_BASE_URL}artists/{artist_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    artist_followers = {}
    artist_followers["popularity"] = result["popularity"]
    artist_followers["follower_count"] = result["followers"]["total"]
    artist_followers["genres"] = result["genres"]
    return artist_followers
