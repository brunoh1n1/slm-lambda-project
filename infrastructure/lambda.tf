# Lambda Function
resource "aws_lambda_function" "tcc_chatbot" {
  function_name = var.function_name
  role         = aws_iam_role.lambda_role.arn
  handler      = "lambda_function.lambda_handler"
  runtime      = "python3.11"
  timeout      = var.lambda_timeout
  memory_size  = var.lambda_memory_size

  # Use container image
  package_type = "Image"
  image_uri    = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_repository_name}:latest"

  environment {
    variables = {
      MODEL_NAME        = var.model_name
      OLLAMA_HOST       = var.ollama_host
      TEMPERATURE       = var.temperature
      MAX_TOKENS        = var.max_tokens
      TCC_MODE          = var.tcc_mode
      ENABLE_STREAMING  = var.enable_streaming
      OLLAMA_CPU_ONLY   = var.ollama_cpu_only
    }
  }

  tags = {
    Name        = var.function_name
    Environment = var.environment
    Project     = "tcc-chatbot"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-role"

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

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.function_name}-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.model_cache.arn}/*"
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days
}

# S3 Bucket for Model Cache
resource "aws_s3_bucket" "model_cache" {
  bucket = "${var.function_name}-model-cache-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.function_name}-model-cache"
    Environment = var.environment
    Project     = "tcc-chatbot"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "model_cache" {
  bucket = aws_s3_bucket.model_cache.id

  rule {
    id     = "delete_old_models"
    status = "Enabled"

    expiration {
      days = 30
    }

    filter {
      prefix = ""
    }
  }
}

# Random string for bucket suffix
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# ECR Repository
resource "aws_ecr_repository" "tcc_chatbot" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = var.ecr_repository_name
    Environment = var.environment
    Project     = "tcc-chatbot"
  }
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "tcc_chatbot" {
  repository = aws_ecr_repository.tcc_chatbot.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}