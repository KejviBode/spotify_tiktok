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
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from botocore.exceptions import ClientError


def send_email_with_pdf(sender_email: str, receiver_emails: list, subject: str, pdf_file_path: str):
    # Create a multipart message object
    message = MIMEMultipart()
    message["Subject"] = subject

    with open(pdf_file_path, "rb") as attachment:
        # Create a MIME base object
        pdf_part = MIMEBase("application", "octet-stream")
        pdf_part.set_payload(attachment.read())
        encoders.encode_base64(pdf_part)
        pdf_part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(pdf_file_path)}",
        )
        pdf_part.add_header(
            "Content-Type",
            "application/pdf"
        )
        message.attach(pdf_part)

    # SES stuff
    client = boto3.client(
        service_name="ses",
        region_name="eu-west-2",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_KEY_ID"]
    )

    try:
        response = client.send_raw_email(
            Source=sender_email,
            Destinations=receiver_emails,
            RawMessage={'Data': message.as_string()}
        )
        print(f"Email Sent to: {receiver_emails}")

    except ClientError as err:
        print(err.args[0])
        return err


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


def event_to_dataframe(event: dict):
    if event is None:
        event = {}
    if event.get("comparison_tracks") == None:
        event["comparison_tracks"] = [{"name": "Shape of You", "artists": "Ed Sheeran"},
                                      {"name": "Bohemian Rhapsody",
                                       "artists": "Queen"},
                                      {"name": "Hello", "artists": "Adele"},
                                      {"name": "Thinking Out Loud",
                                       "artists": "Ed Sheeran"},
                                      {"name": "Smells Like Teen Spirit",
                                       "artists": "Nirvana"},
                                      {"name": "Billie Jean",
                                       "artists": "Michael Jackson"},
                                      {"name": "Hotel California",
                                       "artists": "Eagles"},
                                      {"name": "Rolling in the Deep",
                                       "artists": "Adele"},
                                      {"name": "Hey Jude", "artists": "The Beatles"},
                                      {"name": "Sweet Child o' Mine", "artists": "Guns N' Roses"}]

    comparison_tracks = pd.DataFrame(
        event["comparison_tracks"], columns=['name', 'artists'])
    comparison_tracks = comparison_tracks.rename(
        columns={'name': 'Track Name', 'artists': 'Artist Name(s)'})
    comparison_tracks.reset_index(drop=True)
    return comparison_tracks


def handler(event=None, context=None):
    """Handler function for report generation and SES"""
    try:
        #  prerequisites
        load_dotenv()
        conn = get_db_connection()
        date = dt.datetime.now()
        date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

        # get comparison_tracks from event
        new_tracks_and_artists = event_to_dataframe(event)
        print("Extracted new tracks and artists from event")
        # create dataframes
        df_both = get_average_attributes(
            conn, in_spotify=True, in_tiktok=True)
        df_tiktok = get_average_attributes(
            conn, in_spotify=False, in_tiktok=True)
        print("Created attribute dataframes")
        #  create plotly graphs
        fig_tiktok = px.bar(df_tiktok.melt(), x='variable',
                            y='value', title='Avg attributes for TikTok top 100')
        fig_tiktok.update_yaxes(range=[0, 1])
        fig_tiktok_base64 = base64.b64encode(
            fig_tiktok.to_image()).decode("utf-8")

        fig_both = px.bar(df_both.melt(), x='variable',
                          y='value', title='Avg attributes for Spotify & TikTok top 100')
        fig_both.update_yaxes(range=[0, 1])
        fig_both_base64 = base64.b64encode(fig_both.to_image()).decode("utf-8")
        print("Created attribute px plots")
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
                    <img src="data:image/png;base64,{fig_tiktok_base64}" alt="Spotify Graph">
                    </div>
                    <div class="graph">
                    <img src="data:image/png;base64,{fig_both_base64}" alt="Both Graph">
                    </div>
                </div>
                <div class="table-container">
                    <table id="table1">
                    <thead>
                        <tr>
                            <th>Top 10 tracks and respective artists new to TikTok charts</th>
                        </tr>
                    </thead>
                    <tbody>
                        {new_tracks_and_artists.to_html()}
                    </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
            """

        # export to pdf and save to pdf
        with open("/tmp/report.pdf", "w+b") as result_file:
            # convert HTML to PDF
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=result_file)
        print(pisa_status)
        print("Converted html content to pdf")
        #  push to S3
        bucket_name = 'c7-spotify-tiktok-output'
        session = boto3.Session(
            aws_access_key_id=os.environ["ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["SECRET_KEY_ID"])
        s3 = session.client('s3')

        date = dt.datetime.now()
        date_str = f"{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}"

        file = date_str + '/report.pdf'
        s3.put_object(Body="/tmp/report.pdf", Bucket=bucket_name, Key=file)
        print("PDF uploaded to S3")

        # send pdf as email
        sender_email = "trainee.ilyas.abdulkadir@sigmalabs.co.uk"
        receiver_emails = ["trainee.ilyas.abdulkadir@sigmalabs.co.uk"]
        subject = "Spotify & Tiktok Daily Report"
        pdf_file_path = "/tmp/report.pdf"

        send_email_with_pdf(sender_email, receiver_emails,
                            subject, pdf_file_path)
        if event.get("status_code") != 200:
            message = "LambdaError: Check lambda logs to debug"
        else:
            message = "Success"
        return {
            "status_code": 200,
            "message": message
        }
    except Exception as err:
        return {
            "status_code": 400,
            "message": err.args[0]
        }


if __name__ == "__main__":
    handler()
