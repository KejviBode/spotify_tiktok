"""Daily Lambda"""
import base64
import json
import os
from dotenv import load_dotenv
from requests import post, get
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import operator

from extract_tiktok import match_tiktok_to_spotify, \
    get_tiktok_tracks_api_info, \
    search_multiple_tok_pages


BUCKET_NAME = "c7-spotify-tiktok-output"
SPOTIFY_BASE_URL = "http://api.spotify.com/v1/"
TOP_50_PLAYLIST_ID = "37i9dQZEVXbMDoHDwVN2tF"
TRACK_FILENAME = 'track_ids.csv'
ARTIST_FILENAME = 'artist_ids.csv'
TIKTOK_BASE_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pad/en"
TIKTOK_COOKIE = {"name": "cookie-consent",
                 "value": "{%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22criteo%22:true%2C%22version%22:%22v9%22}"}
AUDIO_FEATURE_KEYS = ["danceability", "energy",
                      "valence", "tempo", "speechiness"]
TOKCHARTS_BASE_URL = "https://tokchart.com/?page="
EVENT_KEYS = ["old_tracks", "old_artists"]


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


def get_spotify_top_50(top_50_uri: str, headers: dict) -> list[dict]:
    '''
    Takes playlist id and returns list of dictionaries of tracks in the playlist
    '''
    result = get(f"{SPOTIFY_BASE_URL}playlists/{top_50_uri}/tracks",
                 headers=headers, timeout=10)
    result = json.loads(result.content)
    return result["items"]


def create_track_dicts(items: list[dict], headers) -> list[dict]:
    '''
    Takes in a list of playlist items and returns a list of dictionaries of each track
    '''
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
            artist_followers = get_artist_genres(artist["id"], headers)
            artist_dict["genres"] = artist_followers["genres"]
            track["artists"].append(artist_dict)
        tracks.append(track)
    return tracks


def get_artist_genres(artist_id: str, headers: dict) -> tuple:
    '''
    Takes an artist id and gets the popularity rating and follower count for that artist
    '''
    result = get(f"{SPOTIFY_BASE_URL}artists/{artist_id}",
                 headers=headers, timeout=10)
    result = json.loads(result.content)
    artist_followers = {}
    artist_followers["genres"] = result["genres"]
    return artist_followers


def get_track_audio_features(track_id: str, headers: dict) -> tuple:
    '''
    Takes a track id and gets danceability, energy, valence, tempo, and speechiness scores
    '''
    result = get(f"{SPOTIFY_BASE_URL}audio-features/{track_id}",
                 headers=headers, timeout=10)
    result = json.loads(result.content)
    audio_features = {}
    audio_features["danceability"] = result["danceability"]
    audio_features["energy"] = result["energy"]
    audio_features["valence"] = result["valence"]
    audio_features["tempo"] = result["tempo"]
    audio_features["speechiness"] = result["speechiness"]
    return audio_features


def get_db_connection():
    '''
    Connects to the database
    '''
    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )
        print("Connected")
        return conn
    except Exception as e:
        print(e)
        print("Error connecting to database.")


def add_track_data(data: list[dict], conn) -> None:
    '''
    Takes in data on tracks and inserts track details into the track table
    '''
    for track in data:
        try:
            with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql_input = "INSERT INTO track (track_name, track_danceability, track_energy, \
                    track_valence, track_tempo, track_speechiness, in_spotify, in_tiktok, \
                        tiktok_rank, spotify_rank, track_spotify_id)\
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
                vals = [track["name"], track["danceability"], track["energy"], track["valence"],
                        track["tempo"], track["speechiness"], track["in_spotify"],
                        track["in_tiktok"], track["tiktok_rank"],
                        track["spotify_rank"], track["id"]]
                cur.execute(sql_input, vals)
                conn.commit()
        except Exception as err:
            print(f"Error for song '{track['name']}' when trying to insert into database\
                  with error: {err.args}")


def add_artist_data(data: list, conn) -> None:
    '''
    Takes in data on tracks and inserts artist details into the artist table
    '''
    for track in data:
        try:
            for artist in track["artists"]:
                with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                    sql_input = "INSERT INTO artist (spotify_name, artist_spotify_id)\
                        VALUES (%s, %s) ON CONFLICT DO NOTHING"
                    vals = [artist["name"], artist["id"]]
                    cur.execute(sql_input, vals)
                    conn.commit()

                for genre in artist["genres"]:
                    genre_id = add_genre(genre, conn)
                    add_artist_genre(genre_id, artist["id"], conn)
                add_track_artist(track["id"], artist["id"], conn)
        except Exception as err:
            print(f"Error for artists in '{track['name']}' when trying to insert into database\
                  with error: {err.args}")


def add_genre(genre_name: str, conn) -> int:
    '''
    Takes in a genre name, adds to the database if not there, and returns genre id
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("INSERT INTO genre (genre_name) VALUES (%s) \
                        ON CONFLICT DO NOTHING", (genre_name,))
        conn.commit()
        cur.execute(
            "SELECT genre_id FROM genre WHERE genre_name = %s", (genre_name,))
        genre_id = cur.fetchone()
    return genre_id['genre_id']


def add_artist_genre(genre_id: int, artist_id: int, conn):
    '''
    Takes in a genre id and artist id and adds them to the artist_genre table
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO artist_genre (genre_id, artist_spotify_id)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [genre_id, artist_id]
        cur.execute(sql_input, vals)
        conn.commit()


def add_track_artist(track_id: int, artist_id: int, conn):
    '''
    Takes in a track id and artist id and adds them to the track_artist table
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO track_artist (track_spotify_id, artist_spotify_id)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [track_id, artist_id]
        cur.execute(sql_input, vals)
        conn.commit()


def get_tiktok_attributes(unmatched_tiktok_songs: list[dict], headers: dict) -> list[dict]:
    '''
    Searches the spotify API for tiktok songs' audio features and adds them to
    their respective dict
    '''
    for track in unmatched_tiktok_songs:
        if "id" not in track.keys():
            print(
                f"Track '{track['name']}'is missing id and cannot be used to find audio features")
        else:
            audio_features = get_track_audio_features(track["id"], headers)
            for key in AUDIO_FEATURE_KEYS:
                if key not in audio_features.keys():
                    print(
                        f"Track '{track['name']}' is missing key: {key} and cannot be used")
            track["danceability"] = audio_features["danceability"]
            track["energy"] = audio_features["energy"]
            track["valence"] = audio_features["valence"]
            track["tempo"] = audio_features["tempo"]
            track["speechiness"] = audio_features["speechiness"]
            for artist in track["artists"]:
                artist_followers = get_artist_genres(artist["id"], headers)
                if "genres" not in artist_followers.keys():
                    continue
                else:
                    artist["genres"] = artist_followers["genres"]
    return unmatched_tiktok_songs


def match_old_tracks_and_artists(old_tracks: dict, old_artists, new_tracks: list[dict]) -> list[dict]:
    '''
    Matches the previous days data with today's extracted data and returns
    a list of tracks that weren't there yesterday
    '''
    if old_tracks is None or old_artists is None:
        return "Couldn't find old tracks and artists :("
    new_to_track_charts = []
    for new_track in new_tracks:
        if "id" not in new_track.keys() or "artists" not in new_track.keys():
            continue
        track_counter = 0
        for old_track in old_tracks:
            if new_track["name"] == old_track[0]:
                track_counter += 1
        if track_counter == 0:
            new_to_track_charts.append(
                {"name": new_track['name'], "artists": new_track["artists"], "tiktok_rank": new_track["tiktok_rank"]})
    new_tiktok_tracks = [
        track for track in new_to_track_charts if track.get("tiktok_rank") != None]
    new_tiktok_tracks = sorted(
        new_tiktok_tracks, key=lambda x: x['tiktok_rank'])
    return new_tiktok_tracks[:10]


def handler(event=None, context=None):
    '''
    Logic to run extraction
    '''
    START = datetime.now()
    try:
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        token = get_auth_token(client_id, client_secret)
        print("Connected to API")
        headers = get_auth_header(token)
        print("Gathering top 50")
        result = get_spotify_top_50(TOP_50_PLAYLIST_ID, headers)
        spotify_tracks = create_track_dicts(result, headers)
        print("Complete!\n")
        print("Fetching html from TikTok charts...")
        tiktok_songs = search_multiple_tok_pages(TOKCHARTS_BASE_URL)
        print(tiktok_songs)
        print("Matching tiktok songs to spotify counterparts...")
        unmatched_tiktok_songs = match_tiktok_to_spotify(
            tiktok_songs, spotify_tracks)
        print("Complete!\n")
        print("Gathering tiktok attributes from spotify api")
        get_tiktok_tracks_api_info(unmatched_tiktok_songs, headers)
        get_tiktok_attributes(unmatched_tiktok_songs, headers)
        print("Complete!\n")
        conn = get_db_connection()
        print("Adding spotify tracks")
        add_track_data(spotify_tracks, conn)
        print("Complete!\n")
        print("Adding spotify artists")
        add_artist_data(spotify_tracks, conn)
        print("Complete!\n")
        print("Adding tiktok songs")
        add_track_data(unmatched_tiktok_songs, conn)
        print("Complete!\n")
        print("Adding tiktok artists")
        add_artist_data(unmatched_tiktok_songs, conn)
        print("Complete!\n")
        spotify_tracks.extend(unmatched_tiktok_songs)
        print("Success!")
        if isinstance(event, dict):
            new_tracks = match_old_tracks_and_artists(
                event["old_tracks"], event["old_artists"], unmatched_tiktok_songs)
        else:
            new_tracks = "Couldn't find old tracks and artists :("
        END = datetime.now()
        PROCESS = END - START
        print(f"Run time: {PROCESS}")
        return {"status_code": 200,
                "message": "Success!",
                "comparison_tracks": new_tracks}
    except Exception as err:
        END = datetime.now()
        PROCESS = END - START
        print(f"Run time: {PROCESS}")
        print(err)
        print({"status_code": 400,
               "message": err.args})
        return {"status_code": 400,
                "message": err.args,
                "comparison_tracks": None}


if __name__ == "__main__":
    handler()
