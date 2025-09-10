#!/bin/bash

# TCC Therapy Chatbot - Test Script
# This script demonstrates how to test the chatbot with different scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8080}"
ENDPOINT="${ENDPOINT:-/inference}"

echo -e "${BLUE}🧠 TCC Therapy Chatbot - Test Suite${NC}"
echo "=================================="
echo "API URL: $API_URL$ENDPOINT"
echo ""

# Test function
test_prompt() {
    local test_name="$1"
    local prompt="$2"
    local expected_keywords="$3"
    
    echo -e "${YELLOW}📝 Test: $test_name${NC}"
    echo "Prompt: $prompt"
    echo ""
    
    response=$(curl -s -X POST "$API_URL$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$prompt\"}")
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Response received${NC}"
        echo "$response" | jq '.'
        
        # Check for expected keywords in response
        if [ -n "$expected_keywords" ]; then
            echo ""
            echo -e "${BLUE}🔍 Checking for keywords: $expected_keywords${NC}"
            if echo "$response" | grep -qi "$expected_keywords"; then
                echo -e "${GREEN}✅ Keywords found in response${NC}"
            else
                echo -e "${YELLOW}⚠️  Keywords not found (this might be normal)${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Request failed${NC}"
    fi
    
    echo ""
    echo "----------------------------------"
    echo ""
}

# Health check
echo -e "${BLUE}🏥 Health Check${NC}"
health_response=$(curl -s "$API_URL/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Service is healthy${NC}"
    echo "$health_response" | jq '.'
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Make sure the service is running on $API_URL"
    exit 1
fi

echo ""
echo "=================================="
echo ""

# Test scenarios
test_prompt "Anxiety Test" \
    "Estou me sentindo muito ansioso hoje, tenho uma apresentação importante amanhã e não consigo parar de pensar que vou falhar" \
    "ansiedade"

test_prompt "Work Stress Test" \
    "Estou passando por um momento difícil no trabalho, me sinto sobrecarregado e não sei como lidar com a pressão" \
    "trabalho"

test_prompt "Social Anxiety Test" \
    "Tenho problemas para me relacionar com outras pessoas, sempre fico preocupado com o que vão pensar de mim" \
    "relacionamento"

test_prompt "Depression Test" \
    "Estou me sentindo muito triste e desanimado, não tenho vontade de fazer nada e me sinto sem esperança" \
    "depressão"

test_prompt "General Help Test" \
    "Estou passando por um momento difícil e preciso de ajuda" \
    "TCC"

# Performance test
echo -e "${BLUE}⚡ Performance Test${NC}"
echo "Testing response time..."

start_time=$(date +%s.%N)
response=$(curl -s -X POST "$API_URL$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Teste de performance"}')
end_time=$(date +%s.%N)

duration=$(echo "$end_time - $start_time" | bc)
echo "Response time: ${duration}s"

if (( $(echo "$duration < 5.0" | bc -l) )); then
    echo -e "${GREEN}✅ Performance is good (< 5s)${NC}"
else
    echo -e "${YELLOW}⚠️  Response time is slow (> 5s)${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All tests completed!${NC}"
echo ""
echo "To test with your own prompts:"
echo "curl -X POST $API_URL$ENDPOINT \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"Your question here\"}'"