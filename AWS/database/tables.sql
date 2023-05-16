DROP TABLE IF EXISTS artist_popularity;
DROP TABLE IF EXISTS track_genre;
DROP TABLE IF EXISTS track_popularity;
DROP TABLE IF EXISTS track_artist;
DROP TABLE IF EXISTS artist;
DROP TABLE IF EXISTS genre;
DROP TABLE IF EXISTS track;

CREATE TABLE IF NOT EXISTS track (
    track_id INT GENERATED ALWAYS AS IDENTITY,
    track_name VARCHAR(200),
    track_danceability INT NOT NULL,
    track_energy INT NOT NULL,
    track_valence INT NOT NULL,
    track_tempo INT NOT NULL,
    track_speechiness INT NOT NULL,
    in_spotify BOOLEAN NOT NULL,
    in_tiktok BOOLEAN NOT NULL DEFAULT false,
    tiktok_rank INT,
    spotify_rank INT,
    spotify_id VARCHAR(200),
    PRIMARY KEY(track_id)
);

CREATE TABLE IF NOT EXISTS artist (
    artist_id INT GENERATED ALWAYS AS IDENTITY,
    spotify_name VARCHAR(100),
    PRIMARY KEY(artist_id)
);

CREATE TABLE IF NOT EXISTS artist_popularity (
    popularity_id INT GENERATED ALWAYS AS IDENTITY,
    artist_id INT NOT NULL,
    follower_count INT NOT NULL,
    recording_at TIMESTAMP NOT NULL,
    PRIMARY KEY(popularity_id),
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id)
);

CREATE TABLE IF NOT EXISTS genre (
    genre_id INT GENERATED ALWAYS AS IDENTITY,
    genre_name VARCHAR(100),
    PRIMARY KEY(genre_id)
);

CREATE TABLE IF NOT EXISTS track_genre (
    track_genre_id INT GENERATED ALWAYS AS IDENTITY,
    track_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY(track_genre_id),
    FOREIGN KEY(track_id) REFERENCES track(track_id),
    FOREIGN KEY(genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE IF NOT EXISTS track_popularity (
    track_popularity_id INT GENERATED ALWAYS AS IDENTITY,
    track_id INT NOT NULL,
    popularity_score INT NOT NULL,
    recording_at TIMESTAMP NOT NULL,
    PRIMARY KEY(track_popularity_id),
    FOREIGN KEY(track_id) REFERENCES track(track_id)
);

CREATE TABLE IF NOT EXISTS track_artist (
    track_artist_id INT GENERATED ALWAYS AS IDENTITY,
    track_id INT NOT NULL,
    artist_id INT NOT NULL,
    FOREIGN KEY(track_id) REFERENCES track(track_id),
    FOREIGN KEY(artist_id) REFERENCES artist(artist_id)
);

