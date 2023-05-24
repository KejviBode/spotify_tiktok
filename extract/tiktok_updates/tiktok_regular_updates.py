import os
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv
from datetime import datetime


TAG_URL = "https://www.tiktok.com/tag/"
ARTIST_URL = "https://www.tiktok.com/@"
METRICS = ["K", "M", "B"]


def get_db_connection() -> connection:
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


def check_metric(text_with_metric: str) -> str:
    if text_with_metric is None:
        return None
    if "K" in text_with_metric:
        return float(float(text_with_metric.split("K")[0]) * 1000/100000)
    elif "M" in text_with_metric:
        return float(float(text_with_metric.split("M")[0]) * (10**6/100000))
    elif "B" in text_with_metric:
        return float(float(text_with_metric.split("B")[0]) * (10**9/100000))
    return None


def load_tiktok_tag_views_url(tag: str) -> str:
    try:
        query_url = f"{TAG_URL}{tag.replace(' ', '%20').lower()}"
        print(query_url)
        req = Request(url=query_url,  headers={
                      'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as page:
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            return soup
    except:
        return None


def load_tag_data(tag_url_soup: BeautifulSoup) -> str:
    if tag_url_soup is None:
        return None
    try:
        views = tag_url_soup.find("h2").find("strong").contents[0]
    except:
        return None
    view_count = check_metric(views)
    if view_count is None:
        return float(views.split(" views")[0])
    else:
        return view_count


def get_db_tracks(conn) -> list[dict]:
    result = None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT * FROM track;"
        cur.execute(sql_query)
        result = cur.fetchall()
    return result


def enrich_track_data(db_tracks: list[dict]) -> list[tuple]:
    tt_track_views_inserts = []
    for track in db_tracks:
        soup = load_tiktok_tag_views_url(track["track_name"])
        view_count = load_tag_data(soup)
        tt_track_views_inserts.append((track["track_spotify_id"], view_count))
    return tt_track_views_inserts


def add_track_views_to_db(enriched_track_data: list[tuple], conn: connection) -> None:
    sql_query = "INSERT INTO tiktok_track_views (track_spotify_id, tiktok_track_views_in_hundred_thousands) VALUES %s"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        execute_values(cur, sql_query, enriched_track_data)
        conn.commit()
    return None


def load_tiktok_artist_url(artist: str) -> BeautifulSoup:
    try:
        query_url = f"{ARTIST_URL}{artist.replace(' ','').lower()}"
        print(query_url)
        req = Request(url=query_url,  headers={
                      'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as page:
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            return soup
    except:
        return None


def load_tiktok_artist_data(artist_url_soup: BeautifulSoup) -> list:
    if artist_url_soup is None:
        return None
    try:
        followers = artist_url_soup.find(
            "strong", {"title": "Followers"}).contents[0]
        follower_count = check_metric(followers)
        if follower_count is None:
            follower_count = int(followers.replace(',', ''))
    except:
        follower_count = None
    try:
        likes = artist_url_soup.find(
            "strong", {"title": "Likes"}).contents[0]
        like_count = check_metric(likes)
        if like_count is None:
            like_count = int(likes.replace(',', ''))
    except:
        like_count = None
    return {"tiktok_follower_count": follower_count, "tiktok_like_count": like_count}


def get_db_artists(conn: connection) -> list[dict]:
    result = None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT * FROM artist;"
        cur.execute(sql_query)
        result = cur.fetchall()
    return result


def enrich_artist_data(db_artists: list[dict]) -> list[tuple]:
    tt_artist_views = []
    for artist in db_artists:
        soup = load_tiktok_artist_url(artist["spotify_name"])
        artist_views = load_tiktok_artist_data(soup)
        if artist_views is None:
            tt_artist_views.append(
                (artist["spotify_name"], None, None))
        else:
            tt_artist_views.append((artist["artist_spotify_id"],
                                    artist_views["tiktok_follower_count"],
                                    artist_views["tiktok_like_count"]))
    return tt_artist_views


def add_artist_views_to_db(enriched_artist_data: list[tuple], conn: connection):
    sql_query = "INSERT INTO tiktok_artist_views (artist_spotify_id, \
        artist_tiktok_follower_count_in_hundred_thousands, artist_tiktok_like_count_in_hundred_thousands) VALUES %s"
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        execute_values(cur, sql_query, enriched_artist_data)
        conn.commit()
    return None


def handler(event=None, context=None):
    START = datetime.now()
    try:
        load_dotenv()
        conn = get_db_connection()
        print("Getting tracks from database...")
        db_tracks = get_db_tracks(conn)
        print("Complete!")
        print("Getting track views from tiktok for each track...")
        enriched_track_data = enrich_track_data(db_tracks)
        print("Complete!")
        print("Inserting track views to db...")
        add_track_views_to_db(enriched_track_data, conn)
        print("Complete!")
        print("Getting artists from database...")
        db_artists = get_db_artists(conn)
        print("Complete!")
        print("Getting artist data from tiktok for each artist...")
        enriched_artist_data = enrich_artist_data(db_artists)
        print("Complete!")
        print("Inserting artist views to db...")
        add_artist_views_to_db(enriched_artist_data, conn)
        print("Complete!")
        END = datetime.now()
        PROCESS = END - START
        print(f"Run time: {PROCESS}")
        return {"status_code": 200,
                "message": "Success!",
                "report_event": event
                }
    except Exception as err:
        END = datetime.now()
        PROCESS = END - START
        print(f"Run time: {PROCESS}")
        print("Error")
        return {"status code": "400",
                "message": err,
                "report_event": event
                }


if __name__ == "__main__":
    print(handler())
