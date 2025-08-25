"""
Unicode-safe comprehensive test for Duck Therapy API
Avoids Unicode encoding issues while testing all functionality
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime


class SafeChatAPITester:
    """Unicode-safe test suite for Duck Therapy Chat API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test-session-{int(time.time())}"
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all test scenarios safely."""
        print("Duck Therapy Chat API Test Suite (Unicode Safe)")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Test sequence
            await self.test_health_check()
            await self.test_send_basic_message()
            await self.test_send_emotional_message()
            await self.test_streaming_basic()
            await self.test_streaming_errors()
            await self.test_streaming_concurrent()
            await self.test_sentiment_validation()
            await self.test_natural_response_validation()
            
        self.print_summary()
    
    async def test_health_check(self):
        """Test server health endpoint."""
        print("\nTesting Health Check...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   SUCCESS: Health check passed")
                    self.log_result("health_check", True, "Server is healthy")
                else:
                    print(f"   FAILED: Health check returned {response.status}")
                    self.log_result("health_check", False, f"Status: {response.status}")
        except Exception as e:
            print(f"   ERROR: Health check failed: {e}")
            self.log_result("health_check", False, str(e))
    
    async def test_send_basic_message(self):
        """Test sending a basic message."""
        print("\nTesting Basic Message...")
        
        message_data = {
            "text": "Hello duck, how are you?",
            "session_id": self.session_id
        }
        
        try:
            async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response_text', '')
                    execution_time = data.get('execution_time_ms', 0)
                    print(f"   SUCCESS: Message processed in {execution_time}ms")
                    print(f"   Response length: {len(response_text)} chars")
                    self.log_result("basic_message", True, f"Response in {execution_time}ms")
                else:
                    print(f"   FAILED: Status {response.status}")
                    self.log_result("basic_message", False, f"Status: {response.status}")
        except Exception as e:
            print(f"   ERROR: {e}")
            self.log_result("basic_message", False, str(e))
    
    async def test_send_emotional_message(self):
        """Test sending an emotional message."""
        print("\nTesting Emotional Message...")
        
        message_data = {
            "text": "I feel very sad and anxious about work stress",
            "session_id": self.session_id,
            "analysis_depth": "detailed"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                if response.status == 200:
                    data = await response.json()
                    emotion_analysis = data.get('emotion_analysis', {})
                    sentiment = emotion_analysis.get('sentiment', 'unknown')
                    execution_time = data.get('execution_time_ms', 0)
                    print(f"   SUCCESS: Emotion processed in {execution_time}ms")
                    print(f"   Detected sentiment: {sentiment}")
                    
                    # Validate sentiment is proper value
                    if sentiment in ['positive', 'negative', 'neutral']:
                        self.log_result("emotional_message", True, f"Sentiment: {sentiment}")
                    else:
                        print(f"   WARNING: Invalid sentiment: {sentiment}")
                        self.log_result("emotional_message", False, f"Invalid sentiment: {sentiment}")
                else:
                    print(f"   FAILED: Status {response.status}")
                    self.log_result("emotional_message", False, f"Status: {response.status}")
        except Exception as e:
            print(f"   ERROR: {e}")
            self.log_result("emotional_message", False, str(e))
    
    async def test_streaming_basic(self):
        """Test basic streaming functionality."""
        print("\nTesting Streaming Basic...")
        
        message_data = {
            "text": "Test streaming response",
            "session_id": f"stream-{self.session_id}"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/chat/stream", json=message_data) as response:
                if response.status == 200:
                    chunk_count = 0
                    chunk_types = []
                    completed = False
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            chunk_count += 1
                            try:
                                data = json.loads(line_str[6:])
                                chunk_type = data.get('type', 'unknown')
                                chunk_types.append(chunk_type)
                                
                                if chunk_type == 'complete':
                                    completed = True
                                    total_time = data.get('total_time_ms', 0)
                                    print(f"   SUCCESS: Streaming completed in {total_time}ms")
                                    break
                                elif chunk_type == 'error':
                                    print(f"   ERROR in stream: {data.get('message', 'Unknown')}")
                                    break
                            except json.JSONDecodeError:
                                print(f"   WARNING: Invalid JSON in chunk {chunk_count}")
                    
                    # Validate streaming completeness
                    expected_types = ['emotion_start', 'emotion_result', 'response_start', 'response_end', 'complete']
                    missing_types = [t for t in expected_types if t not in chunk_types]
                    
                    if completed and not missing_types:
                        print(f"   SUCCESS: All {chunk_count} chunks received correctly")
                        self.log_result("streaming_basic", True, f"All chunks: {chunk_count}")
                    else:
                        print(f"   FAILED: Missing chunks: {missing_types}")
                        self.log_result("streaming_basic", False, f"Missing: {missing_types}")
                else:
                    print(f"   FAILED: Status {response.status}")
                    self.log_result("streaming_basic", False, f"Status: {response.status}")
        except Exception as e:
            print(f"   ERROR: {e}")
            self.log_result("streaming_basic", False, str(e))
    
    async def test_streaming_errors(self):
        """Test streaming error scenarios."""
        print("\nTesting Streaming Errors...")
        
        error_tests = [
            {
                "name": "Empty Message",
                "data": {"text": "", "session_id": "error-test"},
                "expected_status": 422
            },
            {
                "name": "None Session ID", 
                "data": {"text": "test", "session_id": None},
                "expected_status": 422
            }
        ]
        
        passed_tests = 0
        
        for test in error_tests:
            try:
                async with self.session.post(f"{self.base_url}/chat/stream", json=test["data"]) as response:
                    if response.status == test["expected_status"]:
                        print(f"   SUCCESS: {test['name']} correctly returned {response.status}")
                        passed_tests += 1
                    else:
                        print(f"   FAILED: {test['name']} returned {response.status}, expected {test['expected_status']}")
            except Exception as e:
                print(f"   ERROR: {test['name']} - {e}")
        
        if passed_tests == len(error_tests):
            self.log_result("streaming_errors", True, f"All {passed_tests} error tests passed")
        else:
            self.log_result("streaming_errors", False, f"Only {passed_tests}/{len(error_tests)} passed")
    
    async def test_streaming_concurrent(self):
        """Test concurrent streaming."""
        print("\nTesting Streaming Concurrent...")
        
        concurrent_messages = [
            {"text": f"Concurrent test {i}", "session_id": f"concurrent-{i}-{int(time.time())}"}
            for i in range(1, 4)
        ]
        
        async def single_stream(message_data, test_id):
            try:
                async with self.session.post(f"{self.base_url}/chat/stream", json=message_data) as response:
                    if response.status == 200:
                        chunk_count = 0
                        completed = False
                        
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                chunk_count += 1
                                try:
                                    data = json.loads(line_str[6:])
                                    if data.get('type') == 'complete':
                                        completed = True
                                        break
                                except json.JSONDecodeError:
                                    continue
                        
                        return {"id": test_id, "success": completed, "chunks": chunk_count}
                    return {"id": test_id, "success": False, "chunks": 0}
            except Exception as e:
                return {"id": test_id, "success": False, "error": str(e)}
        
        try:
            tasks = [single_stream(msg, i+1) for i, msg in enumerate(concurrent_messages)]
            results = await asyncio.gather(*tasks)
            
            successful = sum(1 for r in results if r.get("success"))
            total = len(results)
            
            print(f"   Concurrent results: {successful}/{total} successful")
            
            if successful == total:
                print(f"   SUCCESS: All concurrent streams completed")
                self.log_result("streaming_concurrent", True, f"All {successful} streams passed")
            else:
                print(f"   FAILED: Only {successful}/{total} streams successful")
                self.log_result("streaming_concurrent", False, f"Only {successful}/{total} passed")
        except Exception as e:
            print(f"   ERROR: {e}")
            self.log_result("streaming_concurrent", False, str(e))
    
    async def test_sentiment_validation(self):
        """Test sentiment validation."""
        print("\nTesting Sentiment Validation...")
        
        test_messages = [
            {"text": "I am very happy today!", "expected_sentiment": "positive"},
            {"text": "I feel sad and depressed", "expected_sentiment": "negative"},
            {"text": "Nothing special today", "expected_sentiment": "neutral"},
            {"text": "Work stress is overwhelming", "expected_sentiment": "negative"},
            {"text": "Thank you for your help!", "expected_sentiment": "positive"}
        ]
        
        passed = 0
        
        for test in test_messages:
            try:
                message_data = {
                    "text": test["text"],
                    "session_id": f"sentiment-test-{int(time.time())}",
                    "analysis_depth": "detailed"
                }
                
                async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        emotion_analysis = data.get('emotion_analysis', {})
                        detected_sentiment = emotion_analysis.get('sentiment', 'unknown')
                        
                        if detected_sentiment in ['positive', 'negative', 'neutral']:
                            print(f"   SUCCESS: '{test['text'][:20]}...' -> {detected_sentiment}")
                            passed += 1
                        else:
                            print(f"   FAILED: Invalid sentiment '{detected_sentiment}' for '{test['text'][:20]}...'")
                    else:
                        print(f"   ERROR: Status {response.status} for sentiment test")
            except Exception as e:
                print(f"   ERROR: Sentiment test failed - {e}")
        
        if passed == len(test_messages):
            print(f"   SUCCESS: All {passed} sentiment tests passed")
            self.log_result("sentiment_validation", True, f"All {passed} tests passed")
        else:
            print(f"   PARTIAL: {passed}/{len(test_messages)} sentiment tests passed")
            self.log_result("sentiment_validation", False, f"Only {passed}/{len(test_messages)} passed")
    
    async def test_natural_response_validation(self):
        """Test natural response validation."""
        print("\nTesting Natural Response Validation...")
        
        test_messages = [
            "Good morning",
            "I feel good today",
            "I am stressed from work",
            "Thank you for chatting with me",
            "I feel anxious and don't know what to do"
        ]
        
        # Analytical phrases that should NOT appear
        forbidden_phrases = [
            "根据你的情绪分析",
            "从你的话中分析",
            "情绪分析显示",
            "分析结果表明",
            "情绪分析结果",
            "分析你的情绪"
        ]
        
        passed = 0
        
        for text in test_messages:
            try:
                message_data = {
                    "text": text,
                    "session_id": f"natural-test-{int(time.time())}",
                    "analysis_depth": "detailed"
                }
                
                async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response_text', '')
                        
                        # Check for forbidden phrases
                        found_forbidden = [phrase for phrase in forbidden_phrases if phrase in response_text]
                        
                        if not found_forbidden:
                            print(f"   SUCCESS: Natural response for '{text[:20]}...'")
                            passed += 1
                        else:
                            print(f"   FAILED: Found analytical phrases in response to '{text[:20]}...'")
                            print(f"           Phrases: {found_forbidden}")
                    else:
                        print(f"   ERROR: Status {response.status} for natural test")
            except Exception as e:
                print(f"   ERROR: Natural test failed - {e}")
        
        if passed == len(test_messages):
            print(f"   SUCCESS: All {passed} natural response tests passed")
            self.log_result("natural_response_validation", True, f"All {passed} tests passed")
        else:
            print(f"   PARTIAL: {passed}/{len(test_messages)} natural response tests passed")
            self.log_result("natural_response_validation", False, f"Only {passed}/{len(test_messages)} passed")
    
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test result."""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if total - passed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        else:
            print("\nAll tests passed successfully!")
        
        print(f"\nTest session: {self.session_id}")


async def main():
    """Main test runner."""
    print("Testing Duck Therapy API with comprehensive validation")
    print("Make sure the backend server is running on http://localhost:8000")
    print("\nStarting tests in 2 seconds...")
    
    await asyncio.sleep(2)
    
    tester = SafeChatAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())