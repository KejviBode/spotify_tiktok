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


data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

#create iam role to define roles
resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# specify lambda function logs aand how long before they are deleted
resource "aws_cloudwatch_log_group" "function_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.update.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

# Allows logs
resource "aws_iam_policy" "function_logging_policy" {
  name = "function-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# attaching iam policy to role
resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.id
  policy_arn = aws_iam_policy.function_logging_policy.arn
}

# trigger schedule 
resource "aws_cloudwatch_event_rule" "hourly_trigger" {
  name                = "spotify_tiktok_hourly_trigger"
  description         = "Update artist followers and popularity"
  schedule_expression = "cron(30 * * * ? *)"
}

# link trigger to lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  arn       = aws_lambda_function.update.arn
  rule      = aws_cloudwatch_event_rule.hourly_trigger.name
  target_id = "songs-hourly-target"
}

#change
resource "aws_lambda_permission" "allow_cloudwatch_to_call_rw_fallout_retry_step_deletion_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.hourly_trigger.arn
}

variable "DB_HOST" {
  type      = string
  sensitive = true
}
variable "DB_NAME" {
  type      = string
  sensitive = true
}
variable "DB_USER" {
  type      = string
  sensitive = true
}
variable "DB_PASSWORD" {
  type      = string
  sensitive = true
}

#definitely change
resource "aws_lambda_function" "update" {
  function_name = "spotify-tiktok-daily-update"
  role          = aws_iam_role.iam_for_lambda.arn
  architectures = ["arm64"]

  package_type = "Image"
  image_uri    = "complete..."

  timeout = 120
  runtime = "nodejs16.x"

  environment {
    variables = {
      DB_PORT     = 5432
      DB_USER     = "postgres"
      DB_HOST     = "complete..."
      DB_NAME     = "production_48_hour"
      DB_PASSWORD = "sigmastudent"
    }
  }
}