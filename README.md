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
- `move_to_long_term`: Contains the backend code for transferring the data from the short-term database to the long-term database.
- `pdf_from_html`: Contains the code for creating a daily pdf report contain information on new tracks in the charts.

## Deployment

1. Clone the repository to your local machine:

git clone https://github.com/KejviBode/spotify_tiktok

## AWS Architecture Setup

Follow the following steps (in order) to set up the architecture required to launch and host the Pipeline on the cloud.

**_note this readme will refer to all files according to their relative paths and lists all commands for the terminal_**

### Steps

#### Step 1

- Navigate to the following directory: architecture
- Execute the following commands:

```
terraform init
terraform apply
```

- This will create the following infrastructure
  - A long term and short term RDS to store data
  - ECR's to store docker images
  - Lambda images which are used in step-functions ones which are triggered by cloudwatch events
  - An S3 bucket where PDF reports will be sent and stored daily
  - And a step-function which runs 4 lambda functions and an SNS in the desired order

**_note: Ensure each file is supplied with a terraform.tfvars file containing all sensitive information such as AWS credentials_**

#### Step 2

- Navigate to the following directories: ["architecture/database", "architecture/long_term_database"]
- Execute the following commands respectively:

```
python3 create_tables.py
```

```
python3 create_long_term_database.py
```

- This will add all the necessary tables for data loading

## Dockerize images

### Spotify-tiktok-daily-report

#### Description of image

This image Produced two plotly bar plots with the average attributes of tracks in the following categories: tracks in only the TikTok top 100 chart and, tracks in both the Spotiify and TikTok top 100 chart.

#### Steps

- Navigate to the following directory: pdf_from_html
- Execute the following commands:

```
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 605126261673.dkr.ecr.eu-west-2.amazonaws.com
docker build --platform "linux/amd64" -t spotify-tiktok-daily-report .
docker tag spotify-tiktok-daily-report:latest 605126261673.dkr.ecr.eu-west-2.amazonaws.com/spotify-tiktok-daily-report:latest
docker push 605126261673.dkr.ecr.eu-west-2.amazonaws.com/spotify-tiktok-daily-report:latest
```

**_note: Ensure each directory has the necessary .env file with the necessary variables_**
