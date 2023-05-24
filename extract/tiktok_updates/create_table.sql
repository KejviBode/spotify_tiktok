CREATE TABLE tiktok_track_views(
    track_spotify_id VARCHAR(200) NOT NULL,
    tiktok_track_views_in_hundred_thousands FLOAT,
    recorded_at TIMESTAMP NOT NULL DEFAULT current_timestamp
)

CREATE TABLE tiktok_artist_views(
    artist_spotify_id VARCHAR(200) NOT NULL,
    artist_tiktok_follower_count_in_hundred_thousands INT,
    artist_tiktok_like_count_in_hundred_thousands INT,
    recorded_at TIMESTAMP NOT NULL DEFAULT current_timestamp
)