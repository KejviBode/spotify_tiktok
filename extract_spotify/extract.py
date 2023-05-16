from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pad/en"
TIKTOK_COOKIE = {"name": "cookie-consent", "value": "{%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22criteo%22:true%2C%22version%22:%22v9%22}"}

def load_tiktok_html_soup(url: str) -> BeautifulSoup:
    '''
    Loads the TikTok charts page and returns a Beautiful Soup object
    '''
    driver = webdriver.Firefox()
    driver.get(BASE_URL)
    driver.add_cookie(TIKTOK_COOKIE)
    got_it_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "detailBtnTips-got--D3sdb")))
    got_it_button.click()
    view_more_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "button--Zmt5a")))
    view_more_button.click()
    for i in range (100):
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
        song_position = song.find("span", {"class": "rankingIndex--CRstI rankingIndex--d5sdy"}).contents[0]
        song_name = song.find("span",{"class":"music-name--Z2hNc music-name--G2iqZ"}).contents[0]
        song_artists = song.find("span", {"class":"auther-name--3HglG auther-name--cXfro"}).contents[0].split("&")
        song_info["song_name"] = song_name
        song_info["song_position"] = song_position
        song_info["artists"] = song_artists
        song_data.append(song_info)
    return song_data

def handler():
    soup = load_tiktok_html_soup(BASE_URL)
    songs = scrape_tiktok_soup(soup)
    print(songs)

if __name__ == "__main__":
    handler()
