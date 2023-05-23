import os
import psycopg2
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection


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


#  prerequisites
load_dotenv()
conn = get_db_connection()

# create dataframes
df_spotify = get_average_attributes(
    conn, in_spotify=True, in_tiktok=False)
df_both = get_average_attributes(conn, in_spotify=True, in_tiktok=True)

#  create plotly graphs
fig_spotify = px.bar(df_spotify.melt(), x='variable',
                     y='value', title='Average Song Attributes for Spotify top 100 tracks')
fig_spotify.update_yaxes(range=[0, 1])

fig_both = px.bar(df_spotify.melt(), x='variable',
                  y='value', title='Average Song Attributes for tracks in both Spotify and TikTok top 100')
fig_both.update_yaxes(range=[0, 1])

#  find new artist data
names = ["Alice", "Bob", "Charlie", "David", "Eva",
         "Frank", "Grace", "Henry", "Ivy", "Jack"]
test_names = pd.DataFrame(names, columns=['Name'])
# html stuff


image_url = 'https://example.com/image.jpg'  # Replace with your image URL
title1 = 'Spotify & TikTok Daily Report'
spotify_attributes = 'Average Attributes of tracks in Spotify charts'
both_attributes = "Average Attributes of tracks in Spotify and TikTok charts"
new_artists = "New artists in charts"
new_tracks = "New tracks in charts"


# Generate the HTML code
html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Spotify & TikTok Report</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
    }}
    
    .container {{
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }}
    
    header {{
      text-align: center;
      margin-bottom: 20px;
    }}
    
    header img {{
      width: 100px;
      height: auto;
    }}
    
    h1 {{
      font-size: 24px;
      margin-bottom: 10px;
    }}
    
    .graph-container {{
      display: flex;
      margin-bottom: 20px;
    }}
    
    .graph {{
      flex: 1;
      border: 1px solid #ccc;
      padding: 10px;
    }}
    
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    
    th, td {{
      border: 1px solid #ccc;
      padding: 8px;
      text-align: left;
    }}
    
    th {{
      background-color: #f2f2f2;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <img src="./spotify.png" alt="Logo">
      <h1>Spotify & TikTok Report</h1>
    </header>
    
    <div class="graph-container">
      <div class="graph" id="graph1">{fig_spotify.to_html()}</div>
      <div class="graph" id="graph2">{fig_both.to_html()}</div>
    </div>
    
    <div class="table-container">
      <table id="table1">{test_names}</table>
      <table id="table2"></table>
    </div>
  </div>
</body>
</html>
"""

# Save the HTML code to a file
with open('graph.html', 'w') as file:
    file.write(html_content)
