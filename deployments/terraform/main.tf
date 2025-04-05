terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "log_group_name" {
  description = "CloudWatch Log Group name pattern"
  type        = string
  default     = "/aws/lambda/*"
}

variable "error_pattern" {
  description = "Error pattern to trigger analysis"
  type        = string
  default     = "ERROR|Exception|5xx|4xx"
}

# EventBridge Rules
resource "aws_cloudwatch_event_rule" "periodic_trigger" {
  name                = "${var.environment}-log-analysis-periodic-trigger"
  description         = "Trigger log analysis every 5 minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_rule" "error_trigger" {
  name          = "${var.environment}-log-analysis-error-trigger"
  description   = "Trigger log analysis on error patterns"
  event_pattern = jsonencode({
    source      = ["aws.logs"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["logs.amazonaws.com"]
      eventName   = ["FilterLogEvents"]
      requestParameters = {
        logGroupName = [var.log_group_name]
        filterPattern = [var.error_pattern]
      }
    }
  })
}

# Step Functions State Machine
resource "aws_sfn_state_machine" "log_analysis_pipeline" {
  name     = "${var.environment}-log-analysis-pipeline"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = templatefile("${path.module}/statemachine/definition.asl.json", {
    collect_logs_function_arn     = aws_lambda_function.collect_logs.arn
    process_chunks_function_arn   = aws_lambda_function.process_chunks.arn
    analyze_with_llm_function_arn = aws_lambda_function.analyze_with_llm.arn
    aggregate_results_function_arn = aws_lambda_function.aggregate_results.arn
    notify_function_arn           = aws_lambda_function.notify.arn
  })
}

# Lambda Functions
resource "aws_lambda_function" "collect_logs" {
  filename         = "functions/collect-logs/dist/index.js"
  function_name    = "${var.environment}-collect-logs"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 300
  memory_size     = 512

  environment {
    variables = {
      LOG_GROUP = var.log_group_name
    }
  }
}

resource "aws_lambda_function" "process_chunks" {
  filename         = "functions/process-chunks/dist/index.js"
  function_name    = "${var.environment}-process-chunks"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 300
  memory_size     = 512
}

resource "aws_lambda_function" "analyze_with_llm" {
  filename         = "functions/analyze-with-llm/dist/index.js"
  function_name    = "${var.environment}-analyze-with-llm"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 300
  memory_size     = 1024

  environment {
    variables = {
      OPENAI_API_KEY     = var.openai_api_key
      ANTHROPIC_API_KEY  = var.anthropic_api_key
    }
  }
}

resource "aws_lambda_function" "aggregate_results" {
  filename         = "functions/aggregate-results/dist/index.js"
  function_name    = "${var.environment}-aggregate-results"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 300
  memory_size     = 512
}

resource "aws_lambda_function" "notify" {
  filename         = "functions/notify/dist/index.js"
  function_name    = "${var.environment}-notify"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }
}

# Supporting Resources
resource "aws_s3_bucket" "log_bucket" {
  bucket = "${var.environment}-log-analysis-${data.aws_caller_identity.current.account_id}"
}

resource "aws_sqs_queue" "analysis_queue" {
  name = "${var.environment}-log-analysis-queue"
}

resource "aws_sqs_queue" "results_queue" {
  name = "${var.environment}-log-results-queue"
}

resource "aws_dynamodb_table" "results_table" {
  name           = "${var.environment}-log-analysis-results"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  range_key      = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }
}

resource "aws_sns_topic" "notification_topic" {
  name = "${var.environment}-log-analysis-notifications"
}

# IAM Roles and Policies
resource "aws_iam_role" "step_functions_role" {
  name = "${var.environment}-log-analysis-step-functions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}-log-analysis-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Data Sources
data "aws_caller_identity" "current" {}

# Outputs
output "log_analysis_pipeline_arn" {
  value = aws_sfn_state_machine.log_analysis_pipeline.arn
}

output "log_bucket_name" {
  value = aws_s3_bucket.log_bucket.id
}

output "results_table_name" {
  value = aws_dynamodb_table.results_table.name
} 