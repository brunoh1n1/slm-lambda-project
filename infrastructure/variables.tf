# General Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Lambda Configuration
variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "tcc-chatbot"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 3008
}

# Model Configuration
variable "model_name" {
  description = "Name of the model to use"
  type        = string
  default     = "tinyllama"
}

variable "ollama_host" {
  description = "Ollama host address"
  type        = string
  default     = "0.0.0.0:11434"
}

variable "temperature" {
  description = "Temperature for text generation"
  type        = number
  default     = 0.7
}

variable "max_tokens" {
  description = "Maximum tokens to generate"
  type        = number
  default     = 512
}

variable "tcc_mode" {
  description = "Enable TCC mode"
  type        = string
  default     = "true"
}

variable "enable_streaming" {
  description = "Enable streaming responses"
  type        = string
  default     = "false"
}

variable "ollama_cpu_only" {
  description = "Use CPU only for Ollama"
  type        = string
  default     = "1"
}

# API Gateway Configuration
variable "api_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "dev"
}

# ECR Configuration
variable "ecr_repository_name" {
  description = "ECR repository name"
  type        = string
  default     = "tcc-chatbot"
}

# Logging Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}