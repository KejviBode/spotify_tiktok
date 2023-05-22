from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import pandas as pd

def get_db_connection():
    """Connects to the database"""
    try:
        conn = psycopg2.connect(
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            host = os.getenv("DB_HOST"),
            port = os.getenv("DB_PORT"),
            database = os.getenv("DB_NAME")
            )
        print("Connected")
        return conn
    except Exception as e:
        print(e)
        print("Error connecting to database.")


def get_top_ten(chart_type: str, conn) -> list[dict]:
    """Finds top 10 entries for Spotify or TikTok and returns a list of dicts"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT t.track_name, t.spotify_rank, t.tiktok_rank, ARRAY_AGG(a.spotify_name) AS spotify_names
            FROM track AS t
            INNER JOIN track_artist AS ta ON t.track_spotify_id = ta.track_spotify_id
            INNER JOIN artist AS a ON ta.artist_spotify_id = a.artist_spotify_id
            WHERE t.{chart_type}_rank BETWEEN 1 AND 10
            GROUP BY t.track_name, t.spotify_rank, t.tiktok_rank
            ORDER BY t.{chart_type}_rank
        """)
        rows = cur.fetchall()

    top_entries = []
    for row in rows:
        track_dict = {
            'track_name': row["track_name"],
            'spotify_rank': row['spotify_rank'] if row['spotify_rank'] is not None else 'N/A',
            'tiktok_rank': row['tiktok_rank'] if row['tiktok_rank'] is not None else 'N/A',
            'spotify_names': ', '.join(row['spotify_names']) if row['spotify_names'] else '',
        }
        top_entries.append(track_dict)

    return top_entries



load_dotenv()
conn = get_db_connection()


def attribute_bar_chart(user_input):
    with conn, conn.cursor() as cur:
        if user_input == "All":
            sql_input = '''
            SELECT
                'In Spotify Charts' AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_speechiness) AS avg_speechiness
            FROM
                track
            WHERE
                in_spotify IS TRUE
            GROUP BY
                situation

            UNION

            SELECT
                'In TikTok Charts' AS situation,
                AVG(track_danceability) AS avg_danceability,
                AVG(track_energy) AS avg_energy,
                AVG(track_valence) AS avg_valence,
                AVG(track_speechiness) AS avg_speechiness
            FROM
                track
            WHERE
                in_tiktok IS TRUE
            GROUP BY
                situation
            '''
            cur.execute(sql_input)
            results = cur.fetchall()

            graph_dicts = []
            for x in range (2):
                graph_dict = {}
                graph_dict["name"] = results[x][0]
                graph_dict["Danceability"] = results[x][1]
                graph_dict["Energy"] = results[x][2]
                graph_dict["Valence"] = results[x][3]
                graph_dict["Speechiness"] = results[x][4]
                graph_dicts.append(graph_dict)
        else:
            if user_input == "Spotify":
                comparison = "TikTok"
            else:
                comparison = "Spotify"

            sql_input = f'''
                SELECT
                    CASE
                        WHEN in_{user_input.lower()} IS TRUE AND in_{comparison.lower()} IS TRUE THEN 'In {comparison} Charts'
                        WHEN in_{user_input.lower()} IS TRUE AND in_{comparison.lower()} IS FALSE THEN 'Not in {comparison} Charts'
                    END AS situation,
                    AVG(track_danceability) AS avg_danceability,
                    AVG(track_energy) AS avg_energy,
                    AVG(track_valence) AS avg_valence,
                    AVG(track_speechiness) AS avg_speechiness
                FROM
                    track
                GROUP BY
                    situation
            '''
            cur.execute(sql_input)
            results = cur.fetchall()

            graph_dicts = []
            for x in range (1, 3):
                graph_dict = {}
                graph_dict["name"] = results[x][0]
                graph_dict["Danceability"] = results[x][1]
                graph_dict["Energy"] = results[x][2]
                graph_dict["Valence"] = results[x][3]
                graph_dict["Speechiness"] = results[x][4]
                graph_dicts.append(graph_dict)
            
            graph_dict = {}
            graph_dict["name"] = "Both"
            graph_dict["Danceability"] = (results[1][1] + results[2][1])/2
            graph_dict["Energy"] = (results[1][2] + results[2][2])/2
            graph_dict["Valence"] = (results[1][3] + results[2][3])/2
            graph_dict["Speechiness"] = (results[1][4] + results[2][4])/2
            graph_dicts.append(graph_dict)

        fig = px.bar(graph_dicts, x='name', y=['Danceability', 'Energy', 'Valence', 'Speechiness'], barmode='group', title='Bar Chart')
        return fig

    

    
attribute_bar_chart("All")
