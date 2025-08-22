# Duck Therapy Chat API Testing Guide

This guide provides comprehensive instructions for testing the Duck Therapy Chat API using multiple approaches.

## Prerequisites

Before running any tests, ensure the following are set up:

### 1. Ollama Server
```bash
# Start Ollama with the Deepseek model
ollama run deepseek-r1-7B-Q5:latest
```

### 2. Backend Server
```bash
# Navigate to backend directory
cd backend

# Start the development server
python start.py

# Verify server is running
curl http://localhost:8000/health
```

### 3. Test Dependencies (for Python tests)
```bash
# Install test dependencies
pip install -r test/requirements.txt
```

## Testing Methods

### Method 1: Python Test Script (Recommended)

The comprehensive Python test script provides automated testing with detailed output.

#### Running the Test Script
```bash
# From the backend directory
cd test
python test_chat_api.py

# Or specify custom server URL
python test_chat_api.py http://localhost:8000
```

#### Features
- ✅ Tests all API endpoints automatically
- ✅ Validates response structure and data
- ✅ Measures performance (execution times)
- ✅ Tests error scenarios
- ✅ Provides detailed summary report
- ✅ Colored output for easy reading

#### Expected Output
```
🦆 Duck Therapy Chat API Test Suite
==================================================

🏥 Testing Health Check
✅ Health check passed: {'status': 'healthy', ...}

💬 Testing Basic Message
✅ Message sent successfully
   📝 Response: 你好！我是鸭鸭，很高兴见到你...
   ⏱️ Execution time: 1245ms
   🤖 LLM used: ['ollama']

... (continues for all tests)

==================================================
🦆 TEST SUMMARY
==================================================
Total Tests: 13
Passed: 13
Failed: 0
Success Rate: 100.0%
```

### Method 2: cURL Commands

Quick and simple command-line testing using curl commands.

#### Running cURL Tests
```bash
# Make script executable (Linux/Mac)
chmod +x test/test_commands.sh

# Run the script
./test/test_commands.sh

# Or run individual commands manually
curl -X POST "http://localhost:8000/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好鸭鸭", "session_id": "test-session"}'
```

#### Features
- ✅ Quick manual testing
- ✅ Easy copy-paste commands
- ✅ JSON response formatting with `jq`
- ✅ HTTP status code checking
- ✅ Works on any platform with curl

### Method 3: Postman Collection

Interactive API testing with a GUI interface.

#### Setting up Postman
1. **Import Collection**
   - Open Postman
   - Click "Import"
   - Select `test/duck_therapy_api.postman_collection.json`

2. **Configure Environment**
   - Create new environment named "Duck Therapy Local"
   - Add variable: `base_url` = `http://localhost:8000`

3. **Run Tests**
   - Select the environment
   - Run individual requests or the entire collection
   - View automated test results in the "Test Results" tab

#### Features
- ✅ GUI-based testing
- ✅ Automated response validation
- ✅ Easy request modification
- ✅ Test result visualization
- ✅ Environment variable management

### Method 4: FastAPI Interactive Docs

Built-in API documentation with testing interface.

#### Accessing Swagger UI
```bash
# With server running, open browser to:
http://localhost:8000/docs
```

#### Features
- ✅ Interactive API documentation
- ✅ Try-it-now functionality
- ✅ Schema validation
- ✅ Response examples
- ✅ Real-time testing

## API Endpoints Reference

### Core Chat Endpoints

#### 1. Send Message
- **Endpoint:** `POST /chat/message`
- **Description:** Send a message to the duck therapy system
- **Required Fields:** `text`, `session_id`
- **Optional Fields:** `context`, `user_preferences`, `workflow_type`, `response_style`, `analysis_depth`

**Example Request:**
```json
{
  "text": "我今天感觉很难过",
  "session_id": "my-session-123",
  "analysis_depth": "detailed"
}
```

**Example Response:**
```json
{
  "message_id": "uuid-string",
  "response_text": "鸭鸭理解你的感受...",
  "emotion_analysis": {
    "sentiment": "negative",
    "emotions": ["sad", "worried"],
    "intensity": 0.7
  },
  "execution_time_ms": 1500,
  "success_rate": 1.0,
  "llm_providers_used": ["ollama"],
  "timestamp": "2025-01-01T12:00:00"
}
```

#### 2. Stream Message
- **Endpoint:** `POST /chat/stream`
- **Description:** Stream real-time response using Server-Sent Events
- **Response Type:** `text/plain` (SSE format)

#### 3. Session Management
- **Get Session:** `GET /chat/session/{session_id}`
- **Get Messages:** `GET /chat/session/{session_id}/messages`
- **Get Emotions:** `GET /chat/session/{session_id}/emotion-history`
- **Clear Session:** `POST /chat/session/{session_id}/clear`
- **Delete Session:** `DELETE /chat/session/{session_id}`
- **List Sessions:** `GET /chat/sessions`

## Expected Response Times

| Operation | Expected Time | Good Performance | Needs Optimization |
|-----------|---------------|------------------|--------------------|
| Basic Message | 1-3 seconds | < 2 seconds | > 5 seconds |
| Emotional Analysis | 2-5 seconds | < 3 seconds | > 8 seconds |
| Session Operations | < 100ms | < 50ms | > 200ms |
| Health Check | < 50ms | < 20ms | > 100ms |

## Common Error Scenarios

### 1. Validation Errors (422)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

**Causes:**
- Empty message text
- Missing required fields
- Invalid field types

### 2. Session Not Found (404)
```json
{
  "detail": "Session not found"
}
```

**Causes:**
- Using non-existent session ID
- Session was deleted

### 3. Workflow Execution Failed (500)
```json
{
  "detail": "Workflow execution failed: Agent processing error"
}
```

**Causes:**
- LLM service unavailable
- Agent configuration issues
- Network connectivity problems

## Troubleshooting

### Issue: Health Check Fails
**Symptoms:** Cannot connect to server
**Solutions:**
1. Verify server is running: `python start.py`
2. Check port availability: `netstat -an | grep 8000`
3. Verify firewall settings

### Issue: LLM Errors
**Symptoms:** 500 errors during message processing
**Solutions:**
1. Check Ollama is running: `ollama ps`
2. Verify model is loaded: `ollama run deepseek-r1-7B-Q5:latest`
3. Check server logs for detailed errors

### Issue: Slow Responses
**Symptoms:** Response times > 10 seconds
**Solutions:**
1. Check system resources (CPU, RAM)
2. Verify Ollama model is properly loaded
3. Consider using a smaller/faster model for testing

### Issue: Connection Refused
**Symptoms:** Cannot connect to localhost:8000
**Solutions:**
1. Ensure backend server is running
2. Check if port 8000 is blocked
3. Try different port in settings

## Performance Testing

### Load Testing with Locust
```python
# Create locustfile.py
from locust import HttpUser, task, between

class ChatAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def send_message(self):
        self.client.post("/chat/message", json={
            "text": "测试消息",
            "session_id": f"load-test-{self.user_id}"
        })

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### Stress Testing Checklist
- [ ] Test with 10 concurrent users
- [ ] Test with 50 concurrent users
- [ ] Test with 100+ concurrent users
- [ ] Monitor response times under load
- [ ] Check for memory leaks
- [ ] Verify error handling under stress

## Continuous Integration

### GitHub Actions Example
```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r test/requirements.txt
      - name: Start Ollama
        run: |
          # Setup Ollama in CI environment
          docker run -d --name ollama ollama/ollama
      - name: Run API tests
        run: python test/test_chat_api.py
```

## Best Practices

### For Development
1. **Run tests before commits** - Ensure API stability
2. **Test error scenarios** - Don't just test happy paths
3. **Monitor performance** - Track response times over time
4. **Use realistic data** - Test with actual Chinese text and emotional content

### For Production
1. **Implement health checks** - Monitor API availability
2. **Set up alerting** - Get notified of failures
3. **Load test regularly** - Ensure performance under real load
4. **Monitor LLM usage** - Track token consumption and costs

## Additional Resources

- **FastAPI Docs:** http://localhost:8000/docs (when server is running)
- **OpenAPI Schema:** http://localhost:8000/openapi.json
- **Health Status:** http://localhost:8000/health
- **Backend Logs:** Check console output when running `python start.py`

---

**Need Help?**
- Check server logs for detailed error messages
- Verify Ollama model is properly loaded
- Ensure all dependencies are installed
- Test with simple messages first before complex scenarios