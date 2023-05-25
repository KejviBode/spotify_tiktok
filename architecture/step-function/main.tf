# basic setup
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

# variables
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
variable "ACCESS_KEY_ID" {
  type      = string
  sensitive = true
}
variable "SECRET_KEY_ID" {
  type      = string
  sensitive = true
}
variable "CLIENT_ID" {
  type      = string
  sensitive = true
}
variable "CLIENT_SECRET" {
  type      = string
  sensitive = true
}
variable "DB_LONG_TERM_HOST" {
  type      = string
  sensitive = true
}
variable "DB_LONG_TERM_NAME" {
  type      = string
  sensitive = true
}

variable "step_function_name" {
  description = "spotify_tiktok_step_function"
  type        = string
  default     = "spotify-tiktok-step-function"
}

# lambda permissions
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

resource "aws_iam_role" "iam_for_lambda" {
  name               = "spotify-tiktok-lambdas"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_cloudwatch_log_group" "function_log_group_spotify_storage" {
  name              = "/aws/lambda/${aws_lambda_function.spotify-tiktok-storage.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_cloudwatch_log_group" "function_log_group_spotify_extract" {
  name              = "/aws/lambda/${aws_lambda_function.spotify-tiktok-extract.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_iam_policy" "function_logging_policy" {
  name = "function-logging-policy-spotify-tiktok"
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

resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.id
  policy_arn = aws_iam_policy.function_logging_policy.arn
}

# lamdba extract spotify stuff
resource "aws_lambda_function" "spotify-tiktok-extract" {
  function_name = "spotify-tiktok-daily-extract"
  role          = aws_iam_role.iam_for_lambda.arn
  architectures = ["x86_64"]

  package_type = "Image"
  image_uri    = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/spotify-tiktok-daily-extraction:latest"

  timeout = 600

  environment {
    variables = {
      DB_PORT       = 5432
      DB_USER       = var.DB_USER
      DB_HOST       = var.DB_HOST
      DB_NAME       = var.DB_NAME
      DB_PASSWORD   = var.DB_PASSWORD
      ACCESS_KEY_ID = var.ACCESS_KEY_ID
      SECRET_KEY_ID = var.SECRET_KEY_ID
      CLIENT_ID     = var.CLIENT_ID
      CLIENT_SECRET = var.CLIENT_SECRET
    }
  }
}

# lambda store stuff
resource "aws_lambda_function" "spotify-tiktok-storage" {
  function_name = "spotify-tiktok-storage"
  role          = aws_iam_role.iam_for_lambda.arn
  architectures = ["x86_64"]

  package_type = "Image"
  image_uri    = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/spotify-tiktok-storage:latest"

  timeout = 600

  environment {
    variables = {
      DB_PORT           = 5432
      DB_USER           = var.DB_USER
      DB_HOST           = var.DB_HOST
      DB_NAME           = var.DB_NAME
      DB_PASSWORD       = var.DB_PASSWORD
      ACCESS_KEY_ID     = var.ACCESS_KEY_ID
      SECRET_KEY_ID     = var.SECRET_KEY_ID
      DB_LONG_TERM_NAME = var.DB_LONG_TERM_NAME
      DB_LONG_TERM_HOST = var.DB_LONG_TERM_HOST
    }
  }
}
# lambda report stuff
resource "aws_lambda_function" "spotify-tiktok-report" {
  function_name = "spotify-tiktok-report"
  role          = aws_iam_role.iam_for_lambda.arn
  architectures = ["x86_64"]

  package_type = "Image"
  image_uri    = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/spotify-tiktok-daily-report:latest"

  memory_size = 1000

  timeout = 600

  environment {
    variables = {
      DB_PORT       = 5432
      DB_USER       = var.DB_USER
      DB_HOST       = var.DB_HOST
      DB_NAME       = var.DB_NAME
      DB_PASSWORD   = var.DB_PASSWORD
      ACCESS_KEY_ID = var.ACCESS_KEY_ID
      SECRET_KEY_ID = var.SECRET_KEY_ID
    }
  }
}
# update spotify
resource "aws_lambda_function" "spotify-tiktok-update-spotify" {
  function_name = "spotify-tiktok-update-spotify"
  role          = aws_iam_role.iam_for_lambda.arn
  architectures = ["x86_64"]

  package_type = "Image"
  image_uri    = "605126261673.dkr.ecr.eu-west-2.amazonaws.com/spotify-tiktok-update-spotify:latest"

  timeout = 600

  environment {
    variables = {
      DB_PORT       = 5432
      DB_USER       = var.DB_USER
      DB_HOST       = var.DB_HOST
      DB_NAME       = var.DB_NAME
      DB_PASSWORD   = var.DB_PASSWORD
      ACCESS_KEY_ID = var.ACCESS_KEY_ID
      SECRET_KEY_ID = var.SECRET_KEY_ID
      CLIENT_ID     = var.CLIENT_ID
      CLIENT_SECRET = var.CLIENT_SECRET
    }
  }
}

# sns topic stuff
resource "aws_sns_topic" "topic" {
  name = "tiktok-tracks-remained-in-top-100"
}

resource "aws_sns_topic_subscription" "ilyas-target" {
  topic_arn = aws_sns_topic.topic.arn
  protocol  = "email"
  endpoint  = "trainee.ilyas.abdulkadir@sigmalabs.co.uk"
}
resource "aws_sns_topic_subscription" "kejve-target" {
  topic_arn = aws_sns_topic.topic.arn
  protocol  = "email"
  endpoint  = "trainee.kejvi.bode@sigmalabs.co.uk"
}
resource "aws_sns_topic_subscription" "selvy-target" {
  topic_arn = aws_sns_topic.topic.arn
  protocol  = "email"
  endpoint  = "trainee.selvy.yasotharan@sigmalabs.co.uk"
}
# sns publish policy

resource "aws_iam_role" "sns_publish_role" {
  name = "spotify-tiktok-sns-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "states.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "sns_publish_policy" {
  name        = "sns-publish-policy"
  description = "Allows publishing messages to the SNS topic"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": [
        "${aws_sns_topic.topic.arn}"
      ]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "sns_publish_attachment" {
  policy_arn = aws_iam_policy.sns_publish_policy.arn
  role       = aws_iam_role.step_function_role.name
}


# step-function stuff
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = var.step_function_name
  role_arn = aws_iam_role.step_function_role.arn

  definition = <<-EOF
  {
    "Comment": "Invoke AWS Lambda from AWS Step Functions with Terraform",
    "StartAt": "Store",
    "States": {
      "Store": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.spotify-tiktok-storage.arn}",
        "Next": "Extract"
      },
      "Extract": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.spotify-tiktok-extract.arn}",
        "Next": "Report"
      },
      "Report": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.spotify-tiktok-report.arn}",
        "Next" : "Update"
      },
      "Update": {
        "Type": "Task",
        "Resource": "${aws_lambda_function.spotify-tiktok-update-spotify.arn}",
        "Next" : "SNS Publish"
      },
      "SNS Publish": {
        "Type": "Task",
        "Resource": "arn:aws:states:::sns:publish",
        "Parameters": {
          "TopicArn": "${aws_sns_topic.topic.arn}",
          "Message.$": "$"
        },
        "End": true
      }
    }
  }
  EOF
}


# Creating iam role to run lambda function
resource "aws_iam_role" "step_function_role" {
  name               = "${var.step_function_name}-role"
  assume_role_policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": ["states.amazonaws.com", "events.amazonaws.com"]
        },
        "Effect": "Allow",
        "Sid": "StepFunctionAssumeRole"
      }
    ]
  }
  EOF
}

#  policy to execute step function
resource "aws_iam_role_policy" "step_function_execution_role_policy" {
  name = "${var.step_function_name}_role_policy"
  role = aws_iam_role.step_function_role.id

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "states:StartExecution"
        ],
        "Resource": "${aws_sfn_state_machine.sfn_state_machine.arn}"
        
      }
    ]
  }
  EOF
}


#  Policy to allow step-func to run lambdas
resource "aws_iam_role_policy" "step_function_policy" {
  name = "${var.step_function_name}-policy"
  role = aws_iam_role.step_function_role.id

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "lambda:InvokeFunction"
        ],
        "Effect": "Allow",
        "Resource": [
          "${aws_lambda_function.spotify-tiktok-extract.arn}",
          "${aws_lambda_function.spotify-tiktok-storage.arn}",
          "${aws_lambda_function.spotify-tiktok-report.arn}",
          "${aws_lambda_function.spotify-tiktok-update-spotify.arn}"
        ]
      }
    ]
  }
  EOF
}


# Scheduling step function
resource "aws_cloudwatch_event_rule" "step_function_schedule" {
  name                = "spotify-daily-step-function"
  description         = "Run step function at 23:55 everyday"
  schedule_expression = "cron(55 23 * * ? *)"
}

# Create event target for step function
resource "aws_cloudwatch_event_target" "target" {
  rule     = aws_cloudwatch_event_rule.step_function_schedule.name
  arn      = aws_sfn_state_machine.sfn_state_machine.arn
  role_arn = aws_iam_role.step_function_role.arn
}