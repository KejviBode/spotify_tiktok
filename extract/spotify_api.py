import os, json
from dotenv import load_dotenv
import base64
from requests import post, get

from pprint import pprint

SPOTIFY_BASE_URL = "http://api.spotify.com/v1/"
TOP_50_PLAYLIST_ID = "37i9dQZEVXbMDoHDwVN2tF"


def get_auth_token() -> str:
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
    """Takes playlist id and returns dictionary of tracks in the playlist"""
    result = get(f"{SPOTIFY_BASE_URL}playlists/{top_50_uri}/tracks", headers=headers, timeout=10)
    result = json.loads(result.content)
    items = result["items"]
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
        track["danceability"] = audio_features[0]
        track["energy"] = audio_features[1]
        track["valence"] = audio_features[2]
        track["tempo"] = audio_features[3]
        track["speechiness"] = audio_features[4]

        track["artists"] = []
        for artist in item["track"]["artists"]:
            artist_dict = {}
            artist_dict["id"] = artist["id"]
            artist_dict["name"] = artist["name"]
            artist_followers = get_artist_followers(artist["id"], headers)
            artist_dict["popularity"] = artist_followers[0]
            artist_dict["follower_count"] = artist_followers[1]
            artist_dict["genres"] = artist_followers[2]
            track["artists"].append(artist_dict)
        tracks.append(track)
    return tracks


def get_artist_followers(artist_id: str, headers: dict) ->tuple:
    """Takes an artist id and gets the popularity rating and follower count for that artist"""
    result = get(f"{SPOTIFY_BASE_URL}artists/{artist_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    popularity = result["popularity"]
    follower_count = result["followers"]["total"]
    genres = result["genres"]
    return (popularity, follower_count, genres)


def get_track_popularity(track_id: str, headers: dict) -> tuple:
    """Takes a track id and gets the popularity rating of that track"""
    result = get(f"{SPOTIFY_BASE_URL}tracks/{track_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    if "popularity" in result:
        popularity = result["popularity"]
    else:
        popularity = None
    return popularity


def get_track_audio_features(track_id: str, headers: dict) -> tuple:
    """Takes a track id and gets danceability, energy, valence, tempo, and speechiness scores"""
    result = get(f"{SPOTIFY_BASE_URL}audio-features/{track_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    danceability = result["danceability"]
    energy = result["energy"]
    valence = result["valence"]
    tempo = result["tempo"]
    speechiness = result["speechiness"]
    return (danceability, energy, valence, tempo, speechiness)


if __name__ == "__main__":
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token = get_auth_token()

    headers = get_auth_header(token)
    result = get_spotify_top_50(TOP_50_PLAYLIST_ID, headers)
    for item in result:
        pprint(item)
        print("   ")
