"""Hourly Lambda"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor


from helper_functions import get_db_connection, get_auth_token, get_auth_header,\
    get_artist_followers, get_track_popularity


def check_database_empty(conn) -> bool:
    '''
    Checks if the database is empty
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_query = "SELECT COUNT(*) FROM track"
        cur.execute(sql_query)
        result = cur.fetchone()
        if result['count'] == 0:
            return True
        else:
            return False


def get_column_values(table_name: str, column_name: str, conn) -> list[int]:
    '''
    Takes a table and column name and returns a list of values from that table column
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = f"SELECT {column_name} FROM {table_name}"
        cur.execute(query)
        values = [row[f'{table_name}_spotify_id'] for row in cur.fetchall()]
    return values


def get_all_popularity(ids: list, headers: str, type: str) -> list[dict]:
    '''
    Takes in a list of ids and returns a list of dicts with popularity data
    '''
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


def add_track_popularity(track_id: int, popularity: int, conn):
    '''
    Takes in a track id and popularity and adds them to the track_popularity table
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO track_popularity (track_spotify_id, popularity_score)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [track_id, popularity]
        cur.execute(sql_input, vals)
        conn.commit()


def add_artist_popularity_data(artist_id: str, popularity: int, follower_count: int, conn):
    '''
    Takes in data on artist popularity and enters into the artist_popularity table
    '''
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO artist_popularity (artist_spotify_id, artist_popularity, \
            follower_count)\
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [artist_id, popularity, follower_count]
        cur.execute(sql_input, vals)
        conn.commit()


def handler(event=None, context=None, callback=None):
    try:
        load_dotenv()
        conn = get_db_connection()
        

        if check_database_empty(conn):
            print("Tracks table currently empty")
        else:
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")


            tracks = get_column_values("track", "track_spotify_id", conn)
            artists = get_column_values("artist", "artist_spotify_id", conn)

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
        return {"status code": "200", "message": "Success!"}
    except Exception as err:
        print("Error")
        return {"status code": "400", "message": err}
        

if __name__ == "__main__":
    handler()
