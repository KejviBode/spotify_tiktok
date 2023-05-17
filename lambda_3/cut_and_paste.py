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

    """
    delete_query = f"""DELETE FROM {table_name}
                    RETURNING *"""

    with conn.cursor() as curs:
        curs.execute(delete_query)
        rows = curs.fetchall()
        columns = [desc[0] for desc in curs.description]
        conn.commit()

    return {
        "data": rows,
        "columns": columns
    }


def put_table_in_csv(fs: S3FileSystem, columns: list[str], rows: list[tuple], table_name: str):
    """

    """
    date = dt.datetime.now()
    date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

    file_path = f"{BUCKET}/{date_str}/table_name.csv"

    with fs.open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)
        writer.writerows(rows)


if __name__ == "__main__":

    pass
