# TOKIFY

## Description

This project gathers data on the top charts from Spotify and TikTok, including chart rankings, track features, and artist popularity. It compares the rankings between the two platforms and visualizes the data using a Dash dashboard. The project is built using Terraform on AWS.

## Features

- Retrieves daily chart rankings for songs from Spotify and TikTok.
- Collects detailed information for each track from the Spotify API, including features, popularity, and artist followers.
- Scrapes artists and track views on TikTok.
- Compares the rankings between Spotify and TikTok.
- Builds a web-based Dash dashboard to visualize the data and rankings comparison.
- Uses Terraform to provision the necessary AWS resources for the project.

## Prerequisites

Before running the project, ensure you have the following:

- Spotify Developer Accounts: Register an application on the Spotify Developer Dashboard to obtain the necessary API credentials.
- AWS Account: Sign up for an AWS account if you don't have one.
- Terraform: Install Terraform on your local machine.

## Project Structure

The project is organized into the following directories:

- `extract`: Contains the backend code for gathering data from the Spotify API and TikTok scraping.
- `dashboard`: Includes the code for the Dash dashboard to visualize the data and rankings comparison.
- `architecture`: Contains the Terraform configuration files to provision the required AWS resources.
- 'move_to_long_term': Contains the backend code for transferring the data from the short-term database to the long-term database.
- 'pdf_from_html': Contains the code for creating a daily pdf report contain information on new tracks in the charts.

## Deployment

1. Clone the repository to your local machine:

git clone https://github.com/KejviBode/spotify_tiktok
