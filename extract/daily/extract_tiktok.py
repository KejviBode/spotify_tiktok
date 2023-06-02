'''Helper functions to scrape tiktok charts webpage'''
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import string
from urllib.request import urlopen, Request

from requests import post, get
import json
import base64


TIKTOK_BASE_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pad/en"
TIKTOK_COOKIE = {"name": "cookie-consent", "value": "{%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22criteo%22:true%2C%22version%22:%22v9%22}"}
ARBITRARY_LIST = [{"name":"Funny son"}, {"name":"Crack Rock"}, {"name":"gobbledeegook"}, {"name":"ghost"}]
SPOTIFY_BASE_URL = "http://api.spotify.com/v1/"
TOKCHARTS_BASE_URL = "https://tokchart.com/?page="


def load_tok_chart_soup(page_num: int, tokchart_url: str = TOKCHARTS_BASE_URL) -> list[BeautifulSoup]:
    '''
    Loads and reads a tokchart page into a BeautifulSoup object
    '''
    try:
        req = Request(url=f"{tokchart_url}{str(page_num)}", headers={'User-Agent': 'Mozilla/5.0'})
    except:
        return None
    with urlopen(req) as page:
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        return soup


def get_tokchart_relevant_div(tok_soup: BeautifulSoup) -> list[dict]:
    '''
    Navigates through the tokchart soup and returns relevant track information
    '''
    soup_div = tok_soup.find_all("div",{"class":"lg:flex sm:flex-col justify-between"})
    song_data = []
    for song in soup_div:
        song_info = {}
        song_name = song.find("h4").find("a").contents[0].strip()
        if "original sound" in song_name:
            continue
        ## This try and except block is here because sometimes the formatting of the css is different
        ## and so the identifier also changes
        try:
            song_rank = song.find("div", {"class": "font-bold sm:font-extrabold text-lg sm:text-2xl"}).contents[0].strip()
        except:
            try:
                song_rank = song.find("div", {"class": "font-bold sm:font-extrabold leading-7 text-base sm:text-xl"}).contents[0].strip()
                # print(song_rank)
            except:
                # print("Are you skipping everything?")
                continue
        try:
            song_artists = song.find("span", {"class": "mt-1 sm:mt-2 text-sm text-gray-500 sm:block sm:text-xl"}).contents[0]
        except:
            song_artists = song.find("span", {"class": "mt-1 sm:mt-2 text-sm text-gray-500 sm:block sm:text-lg"}).contents[0]
        song_info["name"] = song_name.replace("#", "").strip()
        song_info["tiktok_rank"] = song_rank
        song_info["spotify_rank"] = None
        song_info["check_artists"] = [artist.strip() for artist in song_artists.split("&")]
        song_info["in_tiktok"] = True
        song_info["in_spotify"] = False
        song_data.append(song_info)
    return song_data


def search_multiple_tok_pages(base_url: str = TOKCHARTS_BASE_URL) -> list[dict]:
    '''
    Goes through multiple tokchart pages and returns all relevant track information
    '''
    tracks = []
    for i in range(1,12):
        try:
            soup = load_tok_chart_soup(i, base_url)
            if soup is None:
                continue
            track_info = get_tokchart_relevant_div(soup)
            print(track_info)
            [tracks.append(track) for track in track_info]
        except:
            print(f"Error fetching data from {base_url}{i}")
    return tracks


def match_tiktok_to_spotify(tiktok_tracks: list[dict], spotify_tracks: list[dict]) -> list[dict]:
    '''
    Matches songs on tiktok and spotify top charts and 
    return unmatched tiktok songs
    '''
    tiktok_not_on_spotify_chart = []
    for tiktok_track in tiktok_tracks:
        for spotify_track in spotify_tracks:
            if tiktok_track["name"] == spotify_track["name"] or \
                (fuzz.ratio(tiktok_track["name"].lower(), spotify_track["name"].lower())) > 80:
                tiktok_track["in_spotify"] = True
                spotify_track["in_tiktok"] = True
                spotify_track["tiktok_rank"] = tiktok_track["tiktok_rank"]
                break
        if tiktok_track["in_spotify"] is False:
            tiktok_not_on_spotify_chart.append(tiktok_track)
    return tiktok_not_on_spotify_chart
    

def general_api_url_search(track_name: str, artist_names: list[str]) -> str:
    '''
    Returns a query url for spotify api by removing punctuation
    '''
    for i in track_name:
        if i in string.punctuation:
            track_name = track_name.split(i)
            break
    return f"{SPOTIFY_BASE_URL}search/?q=track:{track_name[0]} artist:{artist_names[0]}&type=track&limit=1"


def search_api_track(track_name: str, artist_names: list[str], with_artist: bool, general_search: bool, headers):
    '''
    Searches the spotify API using a tiktok song name and artists' names
    '''
    if with_artist and general_search:
        query_url = general_api_url_search(track_name, artist_names)
    elif with_artist:
        query_url = f"{SPOTIFY_BASE_URL}search/?q=track:{track_name} artist:{','.join(artist_names)}&type=track&limit=1"
    else:
        query_url = f"{SPOTIFY_BASE_URL}search/?q=track:{track_name}&type=track&limit=1"
    print(query_url)
    result = get(query_url, headers=headers)
    try:
        json_result = json.loads(result.content)["tracks"]["items"]
    except:
        json_result = json.loads(result.content)
    return json_result


def attempt_multiple_searches(song_name: str, song_artist: list[str], headers) -> list[dict]:
    '''
    Will search the spotify API multiple times with different query urls
    depending on whether or not it receives a result initially
    '''
    track = search_api_track(song_name, song_artist, True, False, headers)
    if len(track) == 0:
        print(f"Error obtaining track information for: {song_name}")
        print("Attempting to find song in more general terms")
        track = search_api_track(song_name, song_artist, True, True, headers)
    if len(track) == 0:
        print(f"Error obtaining track information for: {song_name} in more general terms")
        print("Attempting to find song exclusively through song name")
        track = search_api_track(song_name, song_artist, False, False,headers)
    if len(track) == 0:
        print(f"Cannot find information for track: {song_name}")
        return None
    if isinstance(track, dict):
        if "error" in track.keys():
            print(f"Cannot find song: {song_name} with artists: {','.join(song_artist)}")
        return None
    if "error" in track[0].keys():
        print(f"Cannot find song: {song_name} with artists: {','.join(song_artist)}")
        return None
    return track


def get_auth_token(client_id, client_secret) -> str:
    '''
    Gets an authorisation token from Spotify API
    '''
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
    '''
    Takes in authorisation token and returns header for API calls
    '''
    return {"Authorization": "Bearer " + token}


def get_tiktok_tracks_api_info(songs: list[dict], headers: dict) -> list[dict]:
    '''
    Iterates through a list of unmatched tiktok songs and finds the track
    information on the spotify API
    '''
    for song in songs:
        track = attempt_multiple_searches(song["name"], song["check_artists"], headers)
        if track is None:
            continue
        else:
            song["id"] = track[0]["id"]
            song["artists"] = []
            for artist in track[0]["artists"]:
                track_artist = {}
                track_artist["name"] = artist["name"]
                track_artist["id"] = artist["id"]
                song["artists"].append(track_artist)
    return songs
