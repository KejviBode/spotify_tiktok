import os
import psycopg2
import s3fs
import csv
import datetime as dt
from s3fs import S3FileSystem
from dotenv import load_dotenv
from psycopg2.extensions import connection

BUCKET = "c7-spotify-tiktok-output"

load_dotenv()


def get_db_connection() -> connection:
    """Connects to the database"""
    try:
        conn = psycopg2.connect(
            user=os.environ["DB_USER"],
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            password=os.environ['DB_PASSWORD'],
            port=os.environ['DB_PORT']
        )
        return conn
    except Exception as err:
        print(err)
        print("Error connecting to database.")


def get_list_from_sql(conn: connection, column_name: str, table_name: str) -> list:

    sql = f"""SELECT {column_name} FROM {table_name};"""
    with conn.cursor() as curs:
        curs.execute(sql, (column_name, table_name))
        tracks = curs.fetchall()
    return tracks


conn = get_db_connection()
old_tracks = get_list_from_sql(conn, "track_name", "track")
print(old_tracks)
