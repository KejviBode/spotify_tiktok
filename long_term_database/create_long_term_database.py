import os
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv


def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(
            user=os.environ["DB_USER"],
            host=os.environ["DB_LONG_TERM_HOST"],
            database=os.environ["DB_LONG_TERM_NAME"],
            password=os.environ['DB_PASSWORD'],
            port=os.environ['DB_PORT']
        )
        return conn
    except Exception as err:
        print(err)
        print("Error connecting to database.")


def create_tables(conn: connection) -> None:
    """Creates tables in the long-term database"""
    with conn.cursor() as cur:
        with open(f"./long_term.sql", "r", encoding='utf-8') as sql:
            cur.execute(sql.read())
    conn.commit()


if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()
    create_tables(conn)