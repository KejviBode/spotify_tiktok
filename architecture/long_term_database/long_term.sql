DROP TABLE IF EXISTS artist_popularity;
DROP TABLE IF EXISTS artist_genre;
DROP TABLE IF EXISTS track_popularity;
DROP TABLE IF EXISTS track_artist;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS track;

CREATE TABLE track (
    track_spotify_id VARCHAR(200) NOT NULL,
    track_name VARCHAR(200) NOT NULL,
    track_danceability FLOAT NOT NULL,
    track_energy FLOAT NOT NULL,
    track_valence FLOAT NOT NULL,
    track_tempo FLOAT NOT NULL,
    track_speechiness FLOAT NOT NULL,
    in_spotify BOOLEAN NOT NULL,
    in_tiktok BOOLEAN NOT NULL,
    tiktok_rank INT,
    spotify_rank INT,
    recorded_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(track_spotify_id)
);

CREATE TABLE artist (
    artist_spotify_id VARCHAR(200) UNIQUE NOT NULL,
    spotify_name VARCHAR(100) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    artist_genres VARCHAR(300),
    PRIMARY KEY(artist_spotify_id)
);

CREATE TABLE artist_popularity (
    popularity_id INT GENERATED ALWAYS AS IDENTITY,
    artist_spotify_id VARCHAR(200) NOT NULL,
    artist_popularity INT NOT NULL,
    follower_count INT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY(popularity_id),
    FOREIGN KEY(artist_spotify_id) REFERENCES artist(artist_spotify_id)
);

CREATE TABLE track_popularity (
    track_popularity_id INT GENERATED ALWAYS AS IDENTITY,
    track_spotify_id VARCHAR(200) NOT NULL,
    popularity_score INT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY(track_popularity_id),
    FOREIGN KEY(track_spotify_id) REFERENCES track(track_spotify_id)
);

CREATE TABLE track_artist (
    track_artist_id INT GENERATED ALWAYS AS IDENTITY,
    track_spotify_id VARCHAR(200) NOT NULL,
    artist_spotify_id VARCHAR(200) NOT NULL,
    PRIMARY KEY(track_artist_id),
    FOREIGN KEY(track_spotify_id) REFERENCES track(track_spotify_id),
    FOREIGN KEY(artist_spotify_id) REFERENCES artist(artist_spotify_id)
);