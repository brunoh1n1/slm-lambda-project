#!/bin/bash

# TCC Therapy Chatbot - Deployment Script
# This script deploys the infrastructure and application to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRASTRUCTURE_DIR="$PROJECT_ROOT/infrastructure"

# Default values
AWS_REGION="us-east-2"
FUNCTION_NAME="tcc-chatbot"
ECR_REPOSITORY="tcc-chatbot"
ENVIRONMENT="dev"

echo -e "${BLUE}🚀 TCC Therapy Chatbot - Deployment Script${NC}"
echo "=============================================="
echo ""

# Check if required tools are installed
check_requirements() {
    echo -e "${YELLOW}🔍 Checking requirements...${NC}"
    
    local missing_tools=()
    
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi
    
    if ! command -v terraform &> /dev/null; then
        missing_tools+=("terraform")
    fi
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required tools: ${missing_tools[*]}${NC}"
        echo "Please install the missing tools and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ All requirements met${NC}"
    echo ""
}

# Get AWS Account ID
get_aws_account_id() {
    echo -e "${YELLOW}🔍 Getting AWS Account ID...${NC}"
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        echo -e "${RED}❌ Failed to get AWS Account ID${NC}"
        echo "Make sure AWS CLI is configured correctly."
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS Account ID: $AWS_ACCOUNT_ID${NC}"
    echo ""
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}🏗️  Deploying infrastructure...${NC}"
    
    cd "$INFRASTRUCTURE_DIR"
    
    # Initialize Terraform
    terraform init
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        echo -e "${YELLOW}📝 Creating terraform.tfvars...${NC}"
        cat > terraform.tfvars << EOF
aws_region     = "$AWS_REGION"
aws_account_id = "$AWS_ACCOUNT_ID"
environment    = "$ENVIRONMENT"
function_name  = "$FUNCTION_NAME"
ecr_repository_name = "$ECR_REPOSITORY"
EOF
    fi
    
    # Plan and apply
    terraform plan -out=tfplan
    terraform apply tfplan
    
    echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
    echo ""
}

# Build and push Docker image
build_and_push_image() {
    echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build image
    docker build -f Dockerfile.lambda -t "$ECR_REPOSITORY:latest" .
    
    # Tag and push
    docker tag "$ECR_REPOSITORY:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest"
    
    echo -e "${GREEN}✅ Docker image built and pushed successfully${NC}"
    echo ""
}

# Update Lambda function
update_lambda() {
    echo -e "${YELLOW}🔄 Updating Lambda function...${NC}"
    
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --image-uri "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest" \
        --region "$AWS_REGION"
    
    echo -e "${GREEN}✅ Lambda function updated successfully${NC}"
    echo ""
}

# Get deployment outputs
get_outputs() {
    echo -e "${YELLOW}📋 Getting deployment outputs...${NC}"
    
    cd "$INFRASTRUCTURE_DIR"
    
    API_URL=$(terraform output -raw api_gateway_url)
    HEALTH_ENDPOINT=$(terraform output -raw health_endpoint)
    INFERENCE_ENDPOINT=$(terraform output -raw inference_endpoint)
    
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Deployment Information:${NC}"
    echo "API Gateway URL: $API_URL"
    echo "Health Endpoint: $HEALTH_ENDPOINT"
    echo "Inference Endpoint: $INFERENCE_ENDPOINT"
    echo ""
    echo -e "${BLUE}🧪 Test your deployment:${NC}"
    echo "curl $HEALTH_ENDPOINT"
    echo "curl -X POST $INFERENCE_ENDPOINT \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"prompt\": \"Estou me sentindo ansioso hoje\"}'"
    echo ""
}

# Main deployment function
main() {
    check_requirements
    get_aws_account_id
    deploy_infrastructure
    build_and_push_image
    update_lambda
    get_outputs
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --function-name)
            FUNCTION_NAME="$2"
            shift 2
            ;;
        --ecr-repository)
            ECR_REPOSITORY="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --region REGION           AWS region (default: us-east-2)"
            echo "  --function-name NAME      Lambda function name (default: tcc-chatbot)"
            echo "  --ecr-repository NAME     ECR repository name (default: tcc-chatbot)"
            echo "  --environment ENV         Environment name (default: dev)"
            echo "  --help                    Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Run main function
main