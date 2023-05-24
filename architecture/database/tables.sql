DROP TABLE IF EXISTS artist_popularity;
DROP TABLE IF EXISTS artist_genre;
DROP TABLE IF EXISTS track_popularity;
DROP TABLE IF EXISTS tiktok_track_views;
DROP TABLE IF EXISTS tiktok_artist_views;
DROP TABLE IF EXISTS track_artist;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS track;


CREATE TABLE IF NOT EXISTS track (
    track_spotify_id VARCHAR(200) NOT NULL,
    track_name VARCHAR(200) NOT NULL,
    track_danceability FLOAT NOT NULL,
    track_energy FLOAT NOT NULL,
    track_valence FLOAT NOT NULL,
    track_tempo FLOAT NOT NULL,
    track_speechiness FLOAT NOT NULL,
    in_spotify BOOLEAN NOT NULL,
    in_tiktok BOOLEAN NOT NULL DEFAULT false,
    tiktok_rank INT,
    spotify_rank INT,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(track_spotify_id)
);

CREATE TABLE IF NOT EXISTS artist (
    artist_spotify_id VARCHAR(200) NOT NULL,
    spotify_name VARCHAR(100) UNIQUE,
    PRIMARY KEY(artist_spotify_id)
);

CREATE TABLE IF NOT EXISTS artist_popularity (
    popularity_id INT GENERATED ALWAYS AS IDENTITY,
    artist_spotify_id VARCHAR(200) NOT NULL,
    artist_popularity INT NOT NULL,
    follower_count INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(popularity_id),
    FOREIGN KEY(artist_spotify_id) REFERENCES artist(artist_spotify_id)
);

CREATE TABLE IF NOT EXISTS genre (
    genre_id INT GENERATED ALWAYS AS IDENTITY,
    genre_name VARCHAR(100) UNIQUE,
    PRIMARY KEY(genre_id)
);

CREATE TABLE IF NOT EXISTS artist_genre (
    artist_genre_id INT GENERATED ALWAYS AS IDENTITY,
    artist_spotify_id VARCHAR(200) NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY(artist_genre_id),
    FOREIGN KEY(artist_spotify_id) REFERENCES artist(artist_spotify_id),
    FOREIGN KEY(genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE IF NOT EXISTS track_popularity (
    track_popularity_id INT GENERATED ALWAYS AS IDENTITY,
    track_spotify_id VARCHAR(200) NOT NULL,
    popularity_score INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(track_popularity_id),
    FOREIGN KEY(track_spotify_id) REFERENCES track(track_spotify_id)
);

CREATE TABLE IF NOT EXISTS track_artist (
    track_artist_id INT GENERATED ALWAYS AS IDENTITY,
    track_spotify_id VARCHAR(200) NOT NULL,
    artist_spotify_id VARCHAR(200) NOT NULL,
    PRIMARY KEY(track_artist_id),
    FOREIGN KEY(track_spotify_id) REFERENCES track(track_spotify_id),
    FOREIGN KEY(artist_spotify_id) REFERENCES artist(artist_spotify_id)
);

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
