#!/bin/bash

# Duck Therapy Chat API - cURL Test Commands
# Make sure the backend server is running before executing these commands

BASE_URL="http://localhost:8000"
SESSION_ID="curl-test-session-$(date +%s)"

echo "🦆 Duck Therapy Chat API - cURL Test Commands"
echo "=============================================="
echo "Base URL: $BASE_URL"
echo "Session ID: $SESSION_ID"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run a test with colored output
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo -e "${BLUE}🧪 Testing: $test_name${NC}"
    echo "Command: $command"
    echo ""
    
    if eval "$command"; then
        echo -e "${GREEN}✅ Success${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
    
    echo ""
    echo "---"
    echo ""
}

# Wait for user confirmation
echo -e "${YELLOW}Make sure the following are running:${NC}"
echo "1. Ollama server with deepseek-r1-7B-Q5:latest model"
echo "2. Duck Therapy backend server at $BASE_URL"
echo ""
read -p "Press Enter to start tests or Ctrl+C to cancel..."
echo ""

# Test 1: Health Check
run_test "Health Check" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" \"$BASE_URL/health\" | jq ."

# Test 2: Send Basic Message
run_test "Send Basic Message" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X POST \"$BASE_URL/chat/message\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"text\": \"你好鸭鸭，我今天感觉很好！\",
    \"session_id\": \"'$SESSION_ID'\"
  }' | jq ."

# Test 3: Send Emotional Message
run_test "Send Emotional Message" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X POST \"$BASE_URL/chat/message\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"text\": \"我今天感觉很难过，工作压力很大，不知道该怎么办\",
    \"session_id\": \"'$SESSION_ID'\",
    \"analysis_depth\": \"detailed\"
  }' | jq ."

# Test 4: Send Message with All Options
run_test "Send Message with Options" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X POST \"$BASE_URL/chat/message\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"text\": \"鸭鸭，我需要一些建议来处理焦虑情绪\",
    \"session_id\": \"'$SESSION_ID'\",
    \"context\": [\"我之前说过我工作压力大\", \"我经常感到焦虑\"],
    \"user_preferences\": {\"tone\": \"gentle\", \"language\": \"chinese\"},
    \"workflow_type\": \"basic_chat_flow\",
    \"response_style\": \"detailed\",
    \"analysis_depth\": \"detailed\"
  }' | jq ."

# Test 5: Get Session Info
run_test "Get Session Info" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" \"$BASE_URL/chat/session/$SESSION_ID\" | jq ."

# Test 6: Get Session Messages
run_test "Get Session Messages" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" \"$BASE_URL/chat/session/$SESSION_ID/messages\" | jq ."

# Test 7: Get Emotion History
run_test "Get Emotion History" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" \"$BASE_URL/chat/session/$SESSION_ID/emotion-history\" | jq ."

# Test 8: List All Sessions
run_test "List All Sessions" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" \"$BASE_URL/chat/sessions\" | jq ."

# Test 9: Stream Message (Server-Sent Events)
run_test "Stream Message" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X POST \"$BASE_URL/chat/stream\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"text\": \"这是一个测试流式响应的消息\",
    \"session_id\": \"stream-'$SESSION_ID'\"
  }' -N"

# Test 10: Clear Session
run_test "Clear Session" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X POST \"$BASE_URL/chat/session/$SESSION_ID/clear\" | jq ."

# Test 11: Delete Session
run_test "Delete Session" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X DELETE \"$BASE_URL/chat/session/$SESSION_ID\" | jq ."

# Error Tests
echo -e "${YELLOW}🚨 Testing Error Scenarios${NC}"

# Test 12: Non-existent Session (should return 404)
run_test "Non-existent Session (404)" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" \"$BASE_URL/chat/session/non-existent-session\""

# Test 13: Empty Message (should return 422)
run_test "Empty Message (422)" "curl -s -w \"\\nHTTP Status: %{http_code}\\n\" -X POST \"$BASE_URL/chat/message\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"text\": \"\",
    \"session_id\": \"error-test\"
  }'"

echo -e "${GREEN}🦆 All cURL tests completed!${NC}"
echo ""
echo -e "${BLUE}📝 Notes:${NC}"
echo "- All successful responses should return HTTP 200"
echo "- Error tests should return their expected status codes"
echo "- Check the JSON responses for proper data structure"
echo "- Stream test shows real-time server-sent events"