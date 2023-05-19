import os
import psycopg2
import s3fs
import csv
import datetime as dt
from s3fs import S3FileSystem
from dotenv import load_dotenv
from psycopg2.extensions import connection

BUCKET = "c7-spotify-tiktok-output"


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


def cut_old_data_from_sql(conn: connection, table_name: str) -> dict[list[tuple], list[str]]:
    """
    Deletes table data for specified table_name in a PostgreSQL database and returns the columns and rows in a dictionary
    """
    delete_query = f"""DELETE FROM {table_name}
                        RETURNING *"""

    with conn.cursor() as curs:
        curs.execute(delete_query)
        rows = curs.fetchall()
        columns = [desc[0] for desc in curs.description]
        conn.commit()

    return {
        "columns": columns,
        "rows": rows
    }


def put_table_in_csv(fs: S3FileSystem, all_data: dict[dict[list[str], list[tuple]]], bucket: str = BUCKET) -> dict:
    """
    Creates a csv file with the necessary columns and rows using the s3fs S3FileSystem
    """
    date = dt.datetime.now()
    date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

    file_path = f"{bucket}/{date_str}/{all_data['table_name']}.csv"

    with fs.open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(all_data['data']['columns'])
        writer.writerows(all_data['data']['rows'])

    print(f"{all_data['table_name']} added to S3 successfully")


def handler(event=None, context=None):
    try:
        load_dotenv()
        conn = get_db_connection()

        fs = s3fs.S3FileSystem(
            key=os.environ["ACCESS_KEY_ID"],
            secret=os.environ["SECRET_KEY_ID"]
        )
        # List of entities in dtabase in order of deletion to prevent Foreign key conflicts
        table_list = ["artist_popularity", "artist_genre",
                      "track_popularity", "track_artist", "artist", "genre", "track"]

        # This retrives all the necessary information for upload to S3
        table_data = [{"table_name": table_name,
                       "data": cut_old_data_from_sql(conn, table_name)} for table_name in table_list]

        # Variable not used for anything, just there so pylint doesn't kick up a fuss
        add_to_csv = [put_table_in_csv(fs, all_data)
                      for all_data in table_data]
        if len(add_to_csv) == 7:
            print("All tables added to S3")
        else:
            print("Failure to upload all tables")

        return {
            'status_code': 200,
            "message": "Success"
        }
    except Exception as err:
        return {
            'status_code': 400,
            "message": err
        }


if __name__ == "__main__":
    handler()
