# Lambda Function Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.tcc_chatbot.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.tcc_chatbot.arn
}

output "lambda_function_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.tcc_chatbot.invoke_arn
}

# API Gateway Outputs
output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.tcc_chatbot.id
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.tcc_chatbot.execution_arn
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.tcc_chatbot.id}.execute-api.${var.aws_region}.amazonaws.com/${var.api_stage_name}"
}

# Health Check Endpoint
output "health_endpoint" {
  description = "Health check endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.tcc_chatbot.id}.execute-api.${var.aws_region}.amazonaws.com/${var.api_stage_name}/health"
}

# Inference Endpoint
output "inference_endpoint" {
  description = "Inference endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.tcc_chatbot.id}.execute-api.${var.aws_region}.amazonaws.com/${var.api_stage_name}/inference"
}

# S3 Bucket Outputs
output "model_cache_bucket_name" {
  description = "Name of the S3 bucket for model cache"
  value       = aws_s3_bucket.model_cache.bucket
}

output "model_cache_bucket_arn" {
  description = "ARN of the S3 bucket for model cache"
  value       = aws_s3_bucket.model_cache.arn
}

# ECR Repository Outputs
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.tcc_chatbot.repository_url
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.tcc_chatbot.arn
}

# CloudWatch Log Groups
output "lambda_log_group_name" {
  description = "Name of the Lambda CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "api_gateway_log_group_name" {
  description = "Name of the API Gateway CloudWatch log group"
  value       = aws_cloudwatch_log_group.api_gateway.name
}