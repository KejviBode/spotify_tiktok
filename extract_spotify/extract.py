
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein
from datetime import datetime

from dotenv import load_dotenv
from requests import post, get
import os, json
import base64


TIKTOK_BASE_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pad/en"
TIKTOK_COOKIE = {"name": "cookie-consent", "value": "{%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22criteo%22:true%2C%22version%22:%22v9%22}"}
ARBITRATY_LIST = [{"name":"Funny son"}, {"name":"Crack Rock"}, {"name":"gobbledeegook"}, {"name":"ghost"}]
SPOTIFY_BASE_URL = "http://api.spotify.com/v1/"


def load_tiktok_html_soup(url: str) -> BeautifulSoup:
    '''
    Loads the TikTok charts page, making it scrapeable using selenium
    and returns a Beautiful Soup object
    '''
    driver = webdriver.Firefox()
    driver.get(url)
    driver.add_cookie(TIKTOK_COOKIE)
    got_it_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "detailBtnTips-got--D3sdb")))
    got_it_button.click()
    view_more_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "button--Zmt5a")))
    view_more_button.click()
    for i in range (10):
        try:
            view_more_button.click()
        except:
            continue
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, "html.parser")
    return soup


def scrape_tiktok_soup(soup: BeautifulSoup) -> list[dict]:
    '''
    Searches the TikTok soup for songs and returns a list of 
    the song's properties
    '''
    song_data = []
    songs = soup.find_all("div", 
                        "sound-item-container--fNzli sound-item-container--Huh+H")
    for song in songs:
        song_info= {}
        song_rank = song.find("span", {"class": "rankingIndex--CRstI rankingIndex--d5sdy"}).contents[0]
        song_name = song.find("span",{"class":"music-name--Z2hNc music-name--G2iqZ"}).contents[0]
        song_artists = song.find("span", {"class":"auther-name--3HglG auther-name--cXfro"}).contents[0].split("&")
        song_info["song_name"] = song_name.replace("#","")
        song_info["song_rank"] = song_rank
        song_info["artists"] = song_artists
        song_info["in_tiktok"] = True
        song_info["in_spotify"] = False
        song_data.append(song_info)
    return song_data


def match_tiktok_to_spotify(tiktok_tracks: list[dict], spotify_tracks: list[dict]) -> list[dict]:
    '''
    Matches songs on tiktok and spotify top charts and 
    return unmatched tiktok songs
    '''
    tiktok_not_on_spotify_chart = []
    for tiktok_track in tiktok_tracks:
        for spotify_track in spotify_tracks:
            if tiktok_track["song_name"] == spotify_track["name"] or \
                (fuzz.ratio(tiktok_track["song_name"].lower(), spotify_track["name"].lower())) > 90:
                tiktok_track["in_spotify"] = True
                spotify_track["in_tiktok"] = True
                spotify_track["tiktok_rank"] = tiktok_track["song_rank"]
                break
        if tiktok_track["in_spotify"] is False:
            tiktok_not_on_spotify_chart.append(tiktok_track)
    return tiktok_not_on_spotify_chart
    

def search_api_track(track_name: str, artist_names: list[str], headers):
    '''
    Searches the spotify API using a tiktok song name and artists' names
    '''
    query_url = f"{SPOTIFY_BASE_URL}search/?q=track:{track_name}&artists:{','.join(artist_names)}&type=track&limit=1"
    result = get(query_url, headers=headers)
    try:
        json_result = json.loads(result.content)["tracks"]["items"]
    except:
        json_result = json.loads(result.content)
    return json_result



def get_auth_token(client_id, client_secret) -> str:
    """Gets an authorisation token from Spotify API"""
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data, timeout=10)
    json_result = json.loads(result.content)
    return json_result["access_token"]

def get_auth_header(token: str) -> dict:
    """Takes in authorisation token and returns header for API calls"""
    return {"Authorization": "Bearer " + token}


def get_tiktok_tracks_api_info(songs: list[dict], headers: dict) -> list[dict]:
    '''
    Iterates through a list of unmatched tiktok songs and finds the track
    information on the spotify API
    '''
    identified_tracks = []
    for song in songs:
        track = search_api_track(song["song_name"], song["artists"], headers)
        if "error" in track[0].keys():
            print(f"Error on song: {song['song_name']} with artists: {','.join(song['artists'])}")
            print(track)
            continue
        identified_tracks.append(track)
    return identified_tracks


def handler():
    '''
    Main script logic
    '''
    START = datetime.now()
    print("Fetching html from TikTok charts...")
    soup = load_tiktok_html_soup(TIKTOK_BASE_URL)
    print("Complete!")
    print("Scraping data from TikTok html...")
    songs = scrape_tiktok_soup(soup)
    print("Complete!")
    print("Matching tiktok songs to spotify counterparts...")
    unmatched_tiktok_songs = match_tiktok_to_spotify(songs, ARBITRATY_LIST)
    print("Complete!")

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token = get_auth_token(client_id, client_secret)
    headers = get_auth_header(token)
    get_tiktok_tracks_api_info(unmatched_tiktok_songs, headers)

    END = datetime.now()
    PROCESS = END - START
    print(f"Run time: {PROCESS}")

if __name__ == "__main__":
    handler()
