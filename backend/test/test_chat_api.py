"""
Comprehensive Test Suite for Duck Therapy Chat API

This script tests all chat API endpoints with various scenarios.
Make sure the backend server is running before executing tests.
"""
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime


class ChatAPITester:
    """Test suite for Duck Therapy Chat API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test-session-{int(time.time())}"
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all test scenarios."""
        print("🦆 Duck Therapy Chat API Test Suite")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Test sequence
            await self.test_health_check()
            await self.test_send_basic_message()
            await self.test_send_emotional_message()
            await self.test_send_message_with_options()
            await self.test_get_session_info()
            await self.test_get_messages()
            await self.test_get_emotion_history()
            await self.test_list_sessions()
            await self.test_streaming_message()
            await self.test_clear_session()
            await self.test_delete_session()
            await self.test_error_scenarios()
            
        self.print_summary()
    
    async def test_health_check(self):
        """Test server health endpoint."""
        print("\n🏥 Testing Health Check")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                    self.log_result("health_check", True, "Server is healthy")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    self.log_result("health_check", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
            self.log_result("health_check", False, str(e))
    
    async def test_send_basic_message(self):
        """Test sending a basic message."""
        print("\n💬 Testing Basic Message")
        
        message_data = {
            "text": "你好鸭鸭，我今天感觉很好！",
            "session_id": self.session_id
        }
        
        await self._test_message_endpoint("/chat/message", message_data, "basic_message")
    
    async def test_send_emotional_message(self):
        """Test sending an emotional message."""
        print("\n😢 Testing Emotional Message")
        
        message_data = {
            "text": "我今天感觉很难过，工作压力很大，不知道该怎么办",
            "session_id": self.session_id,
            "analysis_depth": "detailed"
        }
        
        await self._test_message_endpoint("/chat/message", message_data, "emotional_message")
    
    async def test_send_message_with_options(self):
        """Test sending message with all options."""
        print("\n⚙️ Testing Message with Options")
        
        message_data = {
            "text": "鸭鸭，我需要一些建议来处理焦虑情绪",
            "session_id": self.session_id,
            "context": ["我之前说过我工作压力大", "我经常感到焦虑"],
            "user_preferences": {"tone": "gentle", "language": "chinese"},
            "workflow_type": "basic_chat_flow",
            "response_style": "detailed",
            "analysis_depth": "detailed"
        }
        
        await self._test_message_endpoint("/chat/message", message_data, "message_with_options")
    
    async def test_get_session_info(self):
        """Test getting session information."""
        print("\n📋 Testing Get Session Info")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/session/{self.session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Session info retrieved: {data['message_count']} messages")
                    self.log_result("get_session_info", True, f"Messages: {data['message_count']}")
                else:
                    print(f"❌ Failed to get session info: {response.status}")
                    self.log_result("get_session_info", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Session info error: {e}")
            self.log_result("get_session_info", False, str(e))
    
    async def test_get_messages(self):
        """Test getting session messages."""
        print("\n📝 Testing Get Messages")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/session/{self.session_id}/messages") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Messages retrieved: {data['total_count']} total")
                    self.log_result("get_messages", True, f"Total: {data['total_count']}")
                else:
                    print(f"❌ Failed to get messages: {response.status}")
                    self.log_result("get_messages", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Get messages error: {e}")
            self.log_result("get_messages", False, str(e))
    
    async def test_get_emotion_history(self):
        """Test getting emotion history."""
        print("\n😊 Testing Get Emotion History")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/session/{self.session_id}/emotion-history") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Emotion history retrieved: {data['total_entries']} entries")
                    self.log_result("get_emotion_history", True, f"Entries: {data['total_entries']}")
                else:
                    print(f"❌ Failed to get emotion history: {response.status}")
                    self.log_result("get_emotion_history", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Emotion history error: {e}")
            self.log_result("get_emotion_history", False, str(e))
    
    async def test_list_sessions(self):
        """Test listing all sessions."""
        print("\n📊 Testing List Sessions")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/sessions") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Sessions listed: {data['total_count']} total sessions")
                    self.log_result("list_sessions", True, f"Total: {data['total_count']}")
                else:
                    print(f"❌ Failed to list sessions: {response.status}")
                    self.log_result("list_sessions", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ List sessions error: {e}")
            self.log_result("list_sessions", False, str(e))
    
    async def test_streaming_message(self):
        """Test streaming message endpoint."""
        print("\n🌊 Testing Streaming Message")
        
        message_data = {
            "text": "这是一个测试流式响应的消息",
            "session_id": f"stream-{self.session_id}"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/stream",
                json=message_data
            ) as response:
                if response.status == 200:
                    print("✅ Streaming response started...")
                    chunk_count = 0
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            chunk_count += 1
                            data_str = line_str[6:]  # Remove 'data: ' prefix
                            try:
                                data = json.loads(data_str)
                                print(f"   📦 Chunk {chunk_count}: {data.get('type', 'unknown')}")
                                if data.get('type') == 'end':
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    print(f"✅ Streaming completed with {chunk_count} chunks")
                    self.log_result("streaming_message", True, f"Chunks: {chunk_count}")
                else:
                    print(f"❌ Streaming failed: {response.status}")
                    self.log_result("streaming_message", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            self.log_result("streaming_message", False, str(e))
    
    async def test_clear_session(self):
        """Test clearing a session."""
        print("\n🧹 Testing Clear Session")
        
        try:
            async with self.session.post(f"{self.base_url}/chat/session/{self.session_id}/clear") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Session cleared successfully")
                    self.log_result("clear_session", True, "Session cleared")
                else:
                    print(f"❌ Failed to clear session: {response.status}")
                    self.log_result("clear_session", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Clear session error: {e}")
            self.log_result("clear_session", False, str(e))
    
    async def test_delete_session(self):
        """Test deleting a session."""
        print("\n🗑️ Testing Delete Session")
        
        try:
            async with self.session.delete(f"{self.base_url}/chat/session/{self.session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Session deleted successfully")
                    self.log_result("delete_session", True, "Session deleted")
                else:
                    print(f"❌ Failed to delete session: {response.status}")
                    self.log_result("delete_session", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Delete session error: {e}")
            self.log_result("delete_session", False, str(e))
    
    async def test_error_scenarios(self):
        """Test various error scenarios."""
        print("\n🚨 Testing Error Scenarios")
        
        # Test non-existent session
        try:
            async with self.session.get(f"{self.base_url}/chat/session/non-existent-session") as response:
                if response.status == 404:
                    print("✅ Non-existent session returns 404")
                    self.log_result("error_404_session", True, "Correct 404 response")
                else:
                    print(f"❌ Expected 404, got {response.status}")
                    self.log_result("error_404_session", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Error test failed: {e}")
            self.log_result("error_404_session", False, str(e))
        
        # Test empty message
        try:
            message_data = {
                "text": "",
                "session_id": "error-test-session"
            }
            async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                if response.status == 422:  # Validation error
                    print("✅ Empty message returns 422 validation error")
                    self.log_result("error_empty_message", True, "Correct validation error")
                else:
                    print(f"❌ Expected 422, got {response.status}")
                    self.log_result("error_empty_message", False, f"Status: {response.status}")
        except Exception as e:
            print(f"❌ Empty message test failed: {e}")
            self.log_result("error_empty_message", False, str(e))
    
    async def _test_message_endpoint(self, endpoint: str, message_data: Dict[str, Any], test_name: str):
        """Helper method to test message endpoints."""
        try:
            start_time = time.time()
            async with self.session.post(f"{self.base_url}{endpoint}", json=message_data) as response:
                end_time = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    execution_time = int((end_time - start_time) * 1000)
                    
                    print(f"✅ Message sent successfully")
                    print(f"   📝 Response: {data['response_text'][:100]}...")
                    print(f"   ⏱️ Execution time: {execution_time}ms (API: {data.get('execution_time_ms', 'N/A')}ms)")
                    print(f"   🤖 LLM used: {data.get('llm_providers_used', ['unknown'])}")
                    
                    if data.get('emotion_analysis'):
                        emotions = data['emotion_analysis'].get('emotions', [])
                        sentiment = data['emotion_analysis'].get('sentiment', 'unknown')
                        print(f"   😊 Emotions detected: {emotions} (sentiment: {sentiment})")
                    
                    self.log_result(test_name, True, f"Response in {execution_time}ms")
                else:
                    error_text = await response.text()
                    print(f"❌ Message failed: {response.status}")
                    print(f"   Error: {error_text}")
                    self.log_result(test_name, False, f"Status: {response.status}")
                    
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            self.log_result(test_name, False, str(e))
    
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
        print("\n" + "=" * 50)
        print("🦆 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n✅ All tests completed!")


async def main():
    """Main test runner."""
    import sys
    
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🎯 Testing Duck Therapy API at: {base_url}")
    print("📋 Make sure the following are running:")
    print("   1. Ollama server with deepseek-r1-7B-Q5:latest model")
    print("   2. Duck Therapy backend server")
    print("\n⏳ Starting tests in 3 seconds...")
    
    await asyncio.sleep(3)
    
    tester = ChatAPITester(base_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())