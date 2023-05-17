def get_artist_followers(artist_id: str, headers: dict) ->tuple:
    """Takes an artist id and gets the popularity rating and follower count for that artist"""
    result = get(f"{SPOTIFY_BASE_URL}artists/{artist_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    artist_followers = {}
    artist_followers["popularity"] = result["popularity"]
    artist_followers["follower_count"] = result["followers"]["total"]
    artist_followers["genres"] = result["genres"]
    return artist_followers


def get_track_popularity(track_id: str, headers: dict) -> tuple:
    """Takes a track id and gets the popularity rating of that track"""
    result = get(f"{SPOTIFY_BASE_URL}tracks/{track_id}", headers=headers, timeout=10)
    result = json.loads(result.content)
    if "popularity" in result:
        popularity = result["popularity"]
    else:
        popularity = None
    return popularity

def add_artist_popularity_data(artist_id: str, popularity: int, follower_count: int):
    """Takes in data on artist popularity and enters into the artist_popularity table"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO artist_popularity (artist_spotify_id, artist_popularity, \
            follower_count)\
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"
        vals = [artist_id, popularity, follower_count]
        cur.execute(sql_input, vals)
        conn.commit()


def add_track_popularity(track_id: int, popularity: int):
    """Takes in a track id and popularity and adds them to the track_popularity table"""
    with conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql_input = "INSERT INTO track_popularity (track_spotify_id, popularity_score)\
                    VALUES (%s, %s) ON CONFLICT DO NOTHING"
        vals = [track_id, popularity]
        cur.execute(sql_input, vals)
        conn.commit()
