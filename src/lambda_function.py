import json
import time
import logging
from typing import Dict, Any

from model_manager import ModelManager
from utils import validate_request, format_response

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize model manager
model_manager = ModelManager()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for TCC therapy chatbot
    """
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif event.get('body') is None:
            body = {}
        else:
            body = event.get('body', {})

        # Get HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')

        # Route requests
        if path == '/health' and http_method == 'GET':
            return handle_health()
        elif path == '/inference' and http_method == 'POST':
            return handle_inference(body)
        else:
            return format_response(404, {'error': 'Not found'})

    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return format_response(500, {'error': 'Internal server error'})

def handle_health() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        status = model_manager.get_status()
        return format_response(200, {
            'status': 'healthy',
            'model': model_manager.model_name,
            'model_status': status,
            'timestamp': int(time.time())
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return format_response(500, {'error': 'Health check failed'})

def handle_inference(body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle inference requests"""
    try:
        # Validate request
        validation = validate_request(body)
        if not validation['valid']:
            return format_response(400, {'error': validation['error']})

        # Extract parameters
        prompt = body.get('prompt', '')
        max_tokens = body.get('max_tokens', 512)
        temperature = body.get('temperature', 0.7)

        if not prompt:
            return format_response(400, {'error': 'Prompt is required'})

        # Generate response
        start_time = time.time()
        result = model_manager.generate(prompt, max_tokens, temperature)
        inference_time = time.time() - start_time

        # Format response
        response_data = {
            'response': result['text'],
            'tokens_generated': result.get('tokens_generated', 0),
            'inference_time': round(inference_time, 2),
            'model': model_manager.model_name,
            'timestamp': int(time.time())
        }

        # Add TCC-specific information if available
        if 'tcc_analysis' in result:
            response_data['tcc_analysis'] = result['tcc_analysis']
        if 'homework_suggestions' in result:
            response_data['homework_suggestions'] = result['homework_suggestions']

        return format_response(200, response_data)

    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        return format_response(500, {'error': 'Inference failed'})