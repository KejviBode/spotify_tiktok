import io
import boto3
import os
from matplotlib.backends.backend_pdf import PdfPages
import datetime as dt
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import pandas as pd
import seaborn as sns


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


def get_average_attributes(conn: connection, in_spotify: bool, in_tiktok: bool) -> pd.DataFrame:
    query = """SELECT AVG(track_danceability) AS Danceability,
                AVG(track_energy) AS Energy,
                AVG(track_valence) AS Valence,
                AVG((track_tempo - 50)/200) AS Tempo,
                AVG(track_speechiness) AS Speechiness
                FROM track
                WHERE in_spotify = %s AND in_tiktok = %s"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, (in_spotify, in_tiktok))
        df = pd.DataFrame(cur.fetchall())
    return df


def handler(event=None, context=None):
    # setup
    try:
        load_dotenv()
        conn = get_db_connection()

        # dfs
        df_spotify = get_average_attributes(
            conn, in_spotify=True, in_tiktok=False)
        df_both = get_average_attributes(
            conn, in_spotify=False, in_tiktok=True)

        # Adding graphs to pdf
        with io.BytesIO() as output:
            with PdfPages(output) as pp:

                spotify = sns.barplot(df_spotify)
                spotify.set_title(
                    "Average Attributes of tracks in Spotify charts")
                pp.savefig()

                both = sns.barplot(df_both)
                both.set_title(
                    "Average Attributes of tracks in Spotify and TikTok charts")
                pp.savefig()

            data = output.getvalue()

        bucket_name = 'c7-spotify-tiktok-output'

        session = boto3.Session(
            aws_access_key_id=os.environ["ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["SECRET_KEY_ID"])
        s3 = session.client('s3')

        date = dt.datetime.now()
        date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

        file = date_str + '/report.pdf'
        s3.put_object(Body=data, Bucket=bucket_name, Key=file)
        return {
            "status_code": 200,
            "message": "Success"
        }
    except Exception as err:
        return {
            "status_code": 400,
            "message": err.args[0]
        }


if __name__ == "__main__":
    handler()
