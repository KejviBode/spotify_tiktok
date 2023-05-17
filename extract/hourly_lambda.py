"""Hourly Lambda"""
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from spotify_api import get_db_connection


if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()
