DROP TABLE IF EXISTS artist_popularity;
DROP TABLE IF EXISTS artist_genre;
DROP TABLE IF EXISTS track_popularity;
DROP TABLE IF EXISTS track_artist;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS track;

CREATE TABLE IF NOT EXISTS track (
    track_id INT GENERATED ALWAYS AS IDENTITY,
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
    track_spotify_id VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(track_id)
);

CREATE TABLE IF NOT EXISTS artist (
    artist_id INT GENERATED ALWAYS AS IDENTITY,
    spotify_name VARCHAR(100),
    artist_spotify_id VARCHAR(200) NOT NULL,
    PRIMARY KEY(artist_id)
);

CREATE TABLE IF NOT EXISTS artist_popularity (
    popularity_id INT GENERATED ALWAYS AS IDENTITY,
    artist_id INT NOT NULL,
    artist_popularity INT NOT NULL,
    follower_count INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(popularity_id),
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE IF NOT EXISTS genre (
    genre_id INT GENERATED ALWAYS AS IDENTITY,
    genre_name VARCHAR(100),
    PRIMARY KEY(genre_id)
);

CREATE TABLE IF NOT EXISTS artist_genre (
    artist_genre_id INT GENERATED ALWAYS AS IDENTITY,
    artist_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY(artist_genre_id),
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id),
    FOREIGN KEY(genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE IF NOT EXISTS track_popularity (
    track_popularity_id INT GENERATED ALWAYS AS IDENTITY,
    track_id INT NOT NULL,
    popularity_score INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY(track_popularity_id),
    FOREIGN KEY(track_id) REFERENCES track(track_id)
);

CREATE TABLE IF NOT EXISTS track_artist (
    track_artist_id INT GENERATED ALWAYS AS IDENTITY,
    track_id INT NOT NULL,
    artist_id INT NOT NULL,
    PRIMARY KEY(track_artist_id),
    FOREIGN KEY(track_id) REFERENCES track(track_id),
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id)
);