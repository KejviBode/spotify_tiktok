terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "eu-west-2"
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "track_db_short" {
  identifier             = "spotify-tiktok-tracks-db"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = var.db_username
  password               = var.db_password
  db_name                = "production_48_hour"
  db_subnet_group_name   = "c7-public-db-subnet-group"
  publicly_accessible    = true
  availability_zone      = "eu-west-2a"
  vpc_security_group_ids = ["sg-01745c9fa38b8ed68"]
  skip_final_snapshot    = true
}

resource "aws_db_instance" "track_db_long" {
  identifier             = "spotify-tiktok-tracks-db-long-term"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = var.db_username
  password               = var.db_password
  db_name                = "long_term"
  db_subnet_group_name   = "c7-public-db-subnet-group"
  publicly_accessible    = true
  availability_zone      = "eu-west-2a"
  vpc_security_group_ids = ["sg-01745c9fa38b8ed68"]
  skip_final_snapshot    = true
}
