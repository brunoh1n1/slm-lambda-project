# API Gateway
resource "aws_api_gateway_rest_api" "tcc_chatbot" {
  name        = "${var.function_name}-api"
  description = "API Gateway for TCC Therapy Chatbot"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.function_name}-api"
    Environment = var.environment
    Project     = "tcc-chatbot"
  }
}

# API Gateway Resources
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.tcc_chatbot.id
  parent_id   = aws_api_gateway_rest_api.tcc_chatbot.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_resource" "inference" {
  rest_api_id = aws_api_gateway_rest_api.tcc_chatbot.id
  parent_id   = aws_api_gateway_rest_api.tcc_chatbot.root_resource_id
  path_part   = "inference"
}

# API Gateway Methods
resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.tcc_chatbot.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "inference_post" {
  rest_api_id   = aws_api_gateway_rest_api.tcc_chatbot.id
  resource_id   = aws_api_gateway_resource.inference.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integrations
resource "aws_api_gateway_integration" "health_integration" {
  rest_api_id = aws_api_gateway_rest_api.tcc_chatbot.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.tcc_chatbot.invoke_arn
}

resource "aws_api_gateway_integration" "inference_integration" {
  rest_api_id = aws_api_gateway_rest_api.tcc_chatbot.id
  resource_id = aws_api_gateway_resource.inference.id
  http_method = aws_api_gateway_method.inference_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.tcc_chatbot.invoke_arn
}

# Lambda Permissions
resource "aws_lambda_permission" "api_gateway_health" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tcc_chatbot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tcc_chatbot.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_inference" {
  statement_id  = "AllowExecutionFromAPIGatewayInference"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tcc_chatbot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tcc_chatbot.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "tcc_chatbot" {
  depends_on = [
    aws_api_gateway_integration.health_integration,
    aws_api_gateway_integration.inference_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.tcc_chatbot.id
  stage_name  = var.api_stage_name

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "tcc_chatbot" {
  deployment_id = aws_api_gateway_deployment.tcc_chatbot.id
  rest_api_id   = aws_api_gateway_rest_api.tcc_chatbot.id
  stage_name    = var.api_stage_name

  tags = {
    Name        = "${var.function_name}-stage"
    Environment = var.environment
    Project     = "tcc-chatbot"
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.function_name}-api"
  retention_in_days = var.log_retention_days
}