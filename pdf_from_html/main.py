import os
import psycopg2
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
import datetime as dt
import boto3
from xhtml2pdf import pisa
import base64


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


if __name__ == "__main__":
    #  prerequisites
    load_dotenv()
    conn = get_db_connection()
    date = dt.datetime.now()
    date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

    # create dataframes
    df_spotify = get_average_attributes(
        conn, in_spotify=True, in_tiktok=True)
    df_both = get_average_attributes(conn, in_spotify=False, in_tiktok=True)

    #  create plotly graphs
    fig_spotify = px.bar(df_spotify.melt(), x='variable',
                         y='value', title='Avg attributes for Spotify top 100')
    fig_spotify.update_yaxes(range=[0, 1])
    fig_spotify_base64 = base64.b64encode(
        fig_spotify.to_image()).decode("utf-8")

    fig_both = px.bar(df_both.melt(), x='variable',
                      y='value', title='Avg attributes for Spotify & TikTok top 100')
    fig_both.update_yaxes(range=[0, 1])
    fig_both_base64 = base64.b64encode(fig_both.to_image()).decode("utf-8")

    #  find new artist data
    names = ["Alice", "Bob", "Charlie", "David", "Eva",
             "Frank", "Grace", "Henry", "Ivy", "Jack"]
    test_names = pd.DataFrame(names, columns=['Name'])

    # Generate the HTML code
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Spotify & TikTok Report</title>
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
            width: 300px;
            height: auto;
            }}

            h1 {{
            font-size: 24px;
            margin-bottom: 10px;
            }}

            .graph-container {{
            display: flex;
            margin-bottom: 20px;
            margin: auto;
            }}

            .graph {{
            flex: 1;
            border: 1px solid #ccc;
            padding: 1.5px;
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
            <h1>{f"Spotify & TikTok Report : {date_str}"}</h1>
            </header>

            <div class="graph-container">
            <div class="graph">
                <img src="data:image/png;base64,{fig_spotify_base64}" alt="Spotify Graph">
            </div>
            <div class="graph">
                <img src="data:image/png;base64,{fig_both_base64}" alt="Both Graph">
            </div>
            </div>

            <div class="table-container">
            <table id="table1">
                <thead>
                <tr>
                    <th>New artists</th>
                </tr>
                </thead>
                <tbody>
                {test_names.to_html()}
                </tbody>
            </table>
            <table id="table2">
                <thead>
                <tr>
                    <th>New tracks</th>
                </tr>
                </thead>
                <tbody>
                {test_names.to_html()}
                </tbody>
            </table>
            </div>
        </div>
        </body>
        </html>
        """

   # Save the HTML code to a file
    with open('report.html', 'w') as file:
        file.write(html_content)

    # export to pdf and save to pdf
    with open("report.pdf", "w+b") as result_file:
        # convert HTML to PDF
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=result_file)

    #  push to S3
    bucket_name = 'c7-spotify-tiktok-output'
    session = boto3.Session(
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_KEY_ID"])
    s3 = session.client('s3')

    date = dt.datetime.now()
    date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

    file = date_str + '/report.pdf'
    s3.put_object(Body="./graph.html", Bucket=bucket_name, Key=file)
