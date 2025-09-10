import json
import re
import logging
import time
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def validate_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate inference request
    """
    try:
        # Ensure body is a dictionary
        if not isinstance(body, dict):
            return {'valid': False, 'error': 'Request body must be a JSON object'}
        
        # Check required fields
        if 'prompt' not in body:
            return {'valid': False, 'error': 'Missing required field: prompt'}
        
        prompt = body['prompt']
        if not isinstance(prompt, str) or len(prompt.strip()) == 0:
            return {'valid': False, 'error': 'Prompt must be a non-empty string'}
        
        # Check prompt length
        if len(prompt) > 10000:  # 10KB limit
            return {'valid': False, 'error': 'Prompt too long (max 10KB)'}
        
        # Check optional fields
        if 'max_tokens' in body:
            max_tokens = body['max_tokens']
            if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 2048:
                return {'valid': False, 'error': 'max_tokens must be between 1 and 2048'}
        
        if 'temperature' in body:
            temperature = body['temperature']
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                return {'valid': False, 'error': 'temperature must be between 0 and 2'}
        
        return {'valid': True}
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return {'valid': False, 'error': 'Invalid request format'}

def format_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Lambda response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body)
    }

def handle_errors(error: Exception) -> Dict[str, Any]:
    """
    Handle and format errors
    """
    error_message = str(error)
    
    # Log error details
    logger.error(f"Error: {error_message}")
    
    # Return appropriate error response
    if "timeout" in error_message.lower():
        return format_response(504, {
            'error': 'Request timeout',
            'message': 'The request took too long to process'
        })
    elif "memory" in error_message.lower():
        return format_response(507, {
            'error': 'Insufficient memory',
            'message': 'Not enough memory to process the request'
        })
    else:
        return format_response(500, {
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        })

def sanitize_prompt(prompt: str) -> str:
    """
    Sanitize user input prompt
    """
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', prompt)
    
    # Limit length
    if len(sanitized) > 10000:
        sanitized = sanitized[:10000]
    
    return sanitized.strip()

def calculate_tokens(text: str) -> int:
    """
    Rough token calculation (1 token ≈ 4 characters for English)
    """
    return len(text) // 4

def parse_lambda_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Lambda event and extract relevant information
    """
    try:
        # Handle different event sources
        if 'Records' in event:
            # SQS/SNS event
            return {
                'source': 'sqs',
                'body': event['Records'][0].get('body', '{}')
            }
        elif 'httpMethod' in event or 'requestContext' in event:
            # API Gateway event
            return {
                'source': 'api_gateway',
                'path': event.get('path', ''),
                'method': event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', '')),
                'body': event.get('body', '{}')
            }
        else:
            # Direct invocation
            return {
                'source': 'direct',
                'body': json.dumps(event)
            }
    except Exception as e:
        logger.error(f"Error parsing event: {str(e)}")
        return {
            'source': 'unknown',
            'body': '{}'
        }

def create_error_response(error_code: str, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Create standardized error response
    """
    response = {
        'error': error_code,
        'message': message,
        'timestamp': int(time.time())
    }
    
    if details:
        response['details'] = details
    
    return response

def log_request_info(event: Dict[str, Any], context: Any):
    """
    Log request information for monitoring
    """
    try:
        request_id = context.aws_request_id if context else 'unknown'
        user_agent = event.get('headers', {}).get('User-Agent', 'unknown')
        source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
        
        logger.info(f"Request ID: {request_id}, IP: {source_ip}, User-Agent: {user_agent}")
    except Exception as e:
        logger.error(f"Error logging request info: {str(e)}")

def validate_environment() -> List[str]:
    """
    Validate required environment variables
    """
    required_vars = ['MODEL_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    return missing_vars

def get_model_config() -> Dict[str, Any]:
    """
    Get model configuration from environment
    """
    return {
        'model_name': os.environ.get('MODEL_NAME', 'llama2:7b'),
        'max_tokens': int(os.environ.get('MAX_TOKENS', '512')),
        'temperature': float(os.environ.get('TEMPERATURE', '0.7')),
        'cache_ttl': int(os.environ.get('CACHE_TTL', '3600')),
        's3_bucket': os.environ.get('S3_BUCKET', ''),
        'enable_streaming': os.environ.get('ENABLE_STREAMING', 'false').lower() == 'true'
    }