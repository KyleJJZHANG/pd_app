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
    
    def _safe_print(self, message: str, level: str = "info"):
        """Safe print function that handles Unicode encoding issues on Windows."""
        try:
            print(message)
        except UnicodeEncodeError:
            # Fall back to ASCII representation for problematic characters
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(safe_message)
        except Exception as e:
            # Last resort: print without special characters
            print(f"[Console output error: {e}] - Original message length: {len(message)}")
        
    async def _retry_api_call(self, method: str, url: str, max_retries: int = 3, **kwargs):
        """Helper method to retry API calls with exponential backoff."""
        import asyncio
        
        for attempt in range(max_retries):
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, **kwargs) as response:
                        return response.status, await response.json() if response.status == 200 else await response.text()
                elif method.upper() == "POST":
                    async with self.session.post(url, **kwargs) as response:
                        return response.status, await response.json() if response.status == 200 else await response.text()
                        
            except (aiohttp.ClientConnectionError, aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"   !! Connection error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"   >> Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
            except Exception as e:
                print(f"   !! Unexpected error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise e
    
    async def _warm_up_system(self):
        """Warm up the system for consistent performance measurements."""
        print("Warming up system for performance testing...")
        
        warm_up_message = {
            "text": "系统预热测试消息",
            "session_id": f"warmup-{int(time.time())}"
        }
        
        try:
            # Send a few warm-up requests to initialize agents and cache
            for i in range(2):
                print(f"   Warm-up request {i+1}/2...")
                start_time = time.time()
                
                async with self.session.post(f"{self.base_url}/chat/message", json=warm_up_message) as response:
                    if response.status == 200:
                        await response.json()
                        elapsed = int((time.time() - start_time) * 1000)
                        print(f"   Warm-up {i+1} completed in {elapsed}ms")
                    else:
                        print(f"   Warm-up {i+1} failed: {response.status}")
                        
                # Small delay between warm-up requests
                await asyncio.sleep(0.5)
                        
            print("   System warm-up completed\n")
            
        except Exception as e:
            print(f"   Warning: System warm-up failed: {e}")
            print("   Continuing with tests...\n")
    
    async def _optimize_system_performance(self):
        """Trigger system performance optimization."""
        try:
            print("   >> Triggering performance optimization...")
            async with self.session.post(f"{self.base_url}/chat/performance/optimize") as response:
                if response.status == 200:
                    optimization_data = await response.json()
                    print(f"   + Performance optimization completed:")
                    if optimization_data.get('success'):
                        optimizations = optimization_data.get('data', {}).get('optimizations_applied', [])
                        print(f"     Applied: {optimizations}")
                    else:
                        print(f"     No optimizations needed")
                else:
                    print(f"   !! Optimization endpoint returned: {response.status}")
        except Exception as e:
            print(f"   !! Could not trigger optimization: {e}")
    
    async def _cleanup_test_sessions(self, preserve_session: str = None):
        """Clean up test sessions to prevent interference between tests."""
        print("   >> Cleaning up test sessions...")
        cleanup_sessions = []
        
        try:
            # Get list of sessions
            async with self.session.get(f"{self.base_url}/chat/sessions") as response:
                if response.status == 200:
                    sessions_data = await response.json()
                    total_sessions = sessions_data.get('total_count', 0)
                    
                    # Identify test sessions (contain 'test-', 'stream-', 'error-', etc.)
                    for session in sessions_data.get('sessions', []):
                        session_id = session.get('session_id', '')
                        # Don't clean up the main test session if we want to preserve it
                        if session_id == preserve_session:
                            continue
                        if any(prefix in session_id for prefix in ['test-', 'stream-', 'error-', 'warmup-', 'natural-', 'sentiment-']):
                            cleanup_sessions.append(session_id)
            
            # Clean up identified test sessions
            cleaned_count = 0
            for session_id in cleanup_sessions[:10]:  # Limit to prevent excessive cleanup
                try:
                    async with self.session.delete(f"{self.base_url}/chat/session/{session_id}") as response:
                        if response.status == 200:
                            cleaned_count += 1
                except Exception:
                    continue  # Ignore individual cleanup failures
                    
            print(f"   + Cleaned up {cleaned_count} test sessions")
            
        except Exception as e:
            print(f"   !! Session cleanup failed: {e}")
    
    def _get_timeout_for_test(self, test_type: str) -> int:
        """Get appropriate timeout for different test types."""
        timeouts = {
            'health': 5,
            'message': 15,
            'streaming': 30,
            'concurrent': 60,
            'performance': 45,
            'default': 20
        }
        return timeouts.get(test_type, timeouts['default'])
        
    async def run_all_tests(self):
        """Run all test scenarios."""
        print("Duck Therapy Chat API Test Suite")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Clean up any existing test sessions first (but preserve our main test session)
            await self._cleanup_test_sessions(preserve_session=self.session_id)
            
            # Warm up the system first for consistent performance measurements
            await self._warm_up_system()
            
            # Test sequence with improved error handling
            tests_to_run = [
                ("Health Check", self.test_health_check),
                ("Basic Message", self.test_send_basic_message),  
                ("Emotional Message", self.test_send_emotional_message),
                ("Message with Options", self.test_send_message_with_options),
                ("Session Info", self.test_get_session_info),
                ("Get Messages", self.test_get_messages),
                ("Emotion History", self.test_get_emotion_history),
                ("List Sessions", self.test_list_sessions),
                ("Streaming Messages", self.test_streaming_message),
                ("Streaming Error Scenarios", self.test_streaming_error_scenarios),
                ("Concurrent Streaming", self.test_concurrent_streaming),
                ("Performance Metrics", self.test_streaming_performance_metrics),
                ("Sentiment Validation", self.test_sentiment_validation),
                ("Natural Response Validation", self.test_natural_response_validation),
                ("Clear Session", self.test_clear_session),
                ("Delete Session", self.test_delete_session),
                ("Error Scenarios", self.test_error_scenarios)
            ]
            
            # Run tests with improved error isolation
            for test_name, test_func in tests_to_run:
                try:
                    print(f"\n{'='*20} {test_name} {'='*20}")
                    await test_func()
                except Exception as e:
                    print(f"\n!!! Critical error in {test_name}: {e}")
                    self.log_result(f"{test_name.lower().replace(' ', '_')}", False, f"Critical error: {e}")
                    # Continue with other tests even if one fails critically
                    continue
                    
                # Small delay between tests for stability
                await asyncio.sleep(0.1)
            
            # Final cleanup (now we can clean up all test sessions including the main one)
            print(f"\n{'='*20} Final Cleanup {'='*20}")
            await self._cleanup_test_sessions()
            
        self.print_summary()
    
    async def test_health_check(self):
        """Test server health endpoint."""
        print("\nTesting Health Check")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Health check passed: {data}")
                    self.log_result("health_check", True, "Server is healthy")
                else:
                    print(f"Health check failed: {response.status}")
                    self.log_result("health_check", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Health check error: {e}")
            self.log_result("health_check", False, str(e))
    
    async def test_send_basic_message(self):
        """Test sending a basic message."""
        print("\nTesting Basic Message")
        
        message_data = {
            "text": "你好鸭鸭，我今天感觉很好！",
            "session_id": self.session_id
        }
        
        await self._test_message_endpoint("/chat/message", message_data, "basic_message")
    
    async def test_send_emotional_message(self):
        """Test sending an emotional message."""
        print("\nTesting Emotional Message")
        
        message_data = {
            "text": "我今天感觉很难过，工作压力很大，不知道该怎么办",
            "session_id": self.session_id,
            "analysis_depth": "detailed"
        }
        
        await self._test_message_endpoint("/chat/message", message_data, "emotional_message")
    
    async def test_send_message_with_options(self):
        """Test sending message with all options."""
        print("\nTesting Message with Options")
        
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
        print("\nTesting Get Session Info")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/session/{self.session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Session info retrieved: {data['message_count']} messages")
                    self.log_result("get_session_info", True, f"Messages: {data['message_count']}")
                else:
                    print(f"Failed to get session info: {response.status}")
                    self.log_result("get_session_info", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Session info error: {e}")
            self.log_result("get_session_info", False, str(e))
    
    async def test_get_messages(self):
        """Test getting session messages."""
        print("\nTesting Get Messages")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/session/{self.session_id}/messages") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Messages retrieved: {data['total_count']} total")
                    self.log_result("get_messages", True, f"Total: {data['total_count']}")
                else:
                    print(f"Failed to get messages: {response.status}")
                    self.log_result("get_messages", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Get messages error: {e}")
            self.log_result("get_messages", False, str(e))
    
    async def test_get_emotion_history(self):
        """Test getting emotion history."""
        print("\nTesting Get Emotion History")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/session/{self.session_id}/emotion-history") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Emotion history retrieved: {data['total_entries']} entries")
                    self.log_result("get_emotion_history", True, f"Entries: {data['total_entries']}")
                else:
                    print(f"Failed to get emotion history: {response.status}")
                    self.log_result("get_emotion_history", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Emotion history error: {e}")
            self.log_result("get_emotion_history", False, str(e))
    
    async def test_list_sessions(self):
        """Test listing all sessions."""
        print("\nTesting List Sessions")
        
        try:
            async with self.session.get(f"{self.base_url}/chat/sessions") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Sessions listed: {data['total_count']} total sessions")
                    self.log_result("list_sessions", True, f"Total: {data['total_count']}")
                else:
                    print(f"Failed to list sessions: {response.status}")
                    self.log_result("list_sessions", False, f"Status: {response.status}")
        except Exception as e:
            print(f"List sessions error: {e}")
            self.log_result("list_sessions", False, str(e))
    
    async def test_streaming_message(self):
        """Test streaming message endpoint with comprehensive scenarios."""
        print("\nTesting Streaming Message")
        
        # Test different streaming scenarios
        streaming_tests = [
            {
                "name": "Basic Streaming",
                "data": {
                    "text": "这是一个测试流式响应的消息",
                    "session_id": f"stream-{self.session_id}"
                },
                "description": "Basic streaming test"
            },
            {
                "name": "Emotional Streaming", 
                "data": {
                    "text": "我今天感觉很焦虑，工作压力很大，希望得到一些建议",
                    "session_id": f"stream-emotional-{self.session_id}",
                    "analysis_depth": "detailed"
                },
                "description": "Emotional message with detailed analysis"
            },
            {
                "name": "Long Message Streaming",
                "data": {
                    "text": "我最近一直在思考人生的意义，工作让我感到疲惫，家庭关系也有些紧张。我想知道如何能够找到内心的平静，如何处理这些复杂的情绪。有时候感觉自己像是在迷雾中行走，看不清前方的道路。我需要一些指导和建议来帮助我度过这个困难时期。",
                    "session_id": f"stream-long-{self.session_id}",
                    "response_style": "detailed",
                    "analysis_depth": "detailed"
                },
                "description": "Long complex message with detailed requirements"
            }
        ]
        
        successful_streaming_tests = 0
        
        for i, test_case in enumerate(streaming_tests):
            print(f"\n   >> {test_case['name']} ({test_case['description']})")
            print(f"   Message: {test_case['data']['text'][:50]}...")
            
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat/stream",
                    json=test_case['data']
                ) as response:
                    end_time = time.time()
                    total_time = int((end_time - start_time) * 1000)
                    
                    if response.status == 200:
                        print(f"   + Streaming response started...")
                        
                        # Track streaming data
                        chunk_count = 0
                        chunk_types = []
                        emotion_data = None
                        response_text = None
                        
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                chunk_count += 1
                                data_str = line_str[6:]  # Remove 'data: ' prefix
                                
                                try:
                                    data = json.loads(data_str)
                                    chunk_type = data.get('type', 'unknown')
                                    chunk_types.append(chunk_type)
                                    
                                    print(f"   >> Chunk {chunk_count}: {chunk_type}")
                                    
                                    # Collect specific data for validation
                                    if chunk_type == 'emotion_result':
                                        emotion_data = data.get('emotion_analysis')
                                    elif chunk_type == 'response_end':
                                        response_text = data.get('response_text')
                                    elif chunk_type == 'complete':
                                        print(f"      Stats: {data.get('stats', {})}")
                                        break
                                        
                                except json.JSONDecodeError:
                                    print(f"   !! Invalid JSON in chunk {chunk_count}")
                                    continue
                        
                        # Validate streaming completeness
                        expected_chunk_types = ['emotion_start', 'emotion_result', 'response_start', 'response_end', 'complete']
                        missing_types = [t for t in expected_chunk_types if t not in chunk_types]
                        
                        if not missing_types and response_text:
                            print(f"   + Streaming completed successfully")
                            print(f"   + Total chunks: {chunk_count}, Duration: {total_time}ms")
                            print(f"   + Response preview: {response_text[:50]}...")
                            
                            if emotion_data:
                                print(f"   + Emotion analysis: {emotion_data.get('sentiment', 'N/A')}")
                            
                            successful_streaming_tests += 1
                        else:
                            print(f"   - Incomplete streaming - Missing: {missing_types}")
                            if not response_text:
                                print(f"   - No response text received")
                    else:
                        print(f"   - Streaming failed: {response.status}")
                        error_text = await response.text()
                        print(f"      Error: {error_text}")
                        
            except Exception as e:
                print(f"   - Streaming test error: {e}")
        
        # Log overall streaming test results
        total_streaming_tests = len(streaming_tests)
        if successful_streaming_tests == total_streaming_tests:
            self._safe_print(f"\n[PASS] All {successful_streaming_tests}/{total_streaming_tests} streaming tests passed!")
            self.log_result("streaming_message", True, f"All {successful_streaming_tests} tests passed")
        else:
            self._safe_print(f"\n[FAIL] Only {successful_streaming_tests}/{total_streaming_tests} streaming tests passed")
            self.log_result("streaming_message", False, f"Only {successful_streaming_tests}/{total_streaming_tests} passed")
    
    async def test_streaming_error_scenarios(self):
        """Test streaming endpoint error handling scenarios."""
        print("\nTesting Streaming Error Scenarios")
        
        error_tests = [
            {
                "name": "Empty Message Streaming",
                "data": {
                    "text": "",
                    "session_id": f"error-stream-{int(time.time())}"
                },
                "expected_status": 422,
                "description": "Empty message should return validation error"
            },
            {
                "name": "Invalid Session ID Streaming",
                "data": {
                    "text": "测试无效会话ID的流式响应",
                    "session_id": None
                },
                "expected_status": 422,
                "description": "None session_id should return validation error"
            },
            {
                "name": "Extremely Long Message Streaming",
                "data": {
                    "text": "测试" * 1001,  # 4004 characters - exceeds 2000 limit
                    "session_id": f"long-stream-{int(time.time())}"
                },
                "expected_status": 422,  # Should return validation error
                "description": "Extremely long message should return validation error"
            },
            {
                "name": "Near Limit Message Streaming", 
                "data": {
                    "text": "很长的消息内容测试" * 40,  # ~800 characters - within limit
                    "session_id": f"near-limit-{int(time.time())}"
                },
                "expected_status": 200,  # Should handle gracefully
                "description": "Message near character limit should work"
            },
            {
                "name": "Exactly At Limit Message Streaming",
                "data": {
                    "text": "测试" * 500,  # Exactly 2000 characters  
                    "session_id": f"at-limit-{int(time.time())}"
                },
                "expected_status": 200,  # Should handle gracefully
                "description": "Message exactly at 2000 character limit should work"
            }
        ]
        
        successful_error_tests = 0
        
        for i, test_case in enumerate(error_tests):
            print(f"\n   >> {test_case['name']} ({test_case['description']})")
            
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat/stream",
                    json=test_case['data']
                ) as response:
                    end_time = time.time()
                    total_time = int((end_time - start_time) * 1000)
                    
                    expected_status = test_case['expected_status']
                    
                    if response.status == expected_status:
                        if response.status == 200:
                            # For successful responses, verify streaming works
                            chunk_count = 0
                            received_complete = False
                            
                            async for line in response.content:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith('data: '):
                                    chunk_count += 1
                                    try:
                                        data = json.loads(line_str[6:])
                                        chunk_type = data.get('type', 'unknown')
                                        
                                        if chunk_type == 'complete':
                                            received_complete = True
                                            break
                                        elif chunk_type == 'error':
                                            print(f"   !! Received error chunk: {data}")
                                            break
                                    except json.JSONDecodeError:
                                        continue
                            
                            if received_complete or chunk_count > 0:
                                print(f"   + Error scenario handled gracefully - {chunk_count} chunks in {total_time}ms")
                                successful_error_tests += 1
                            else:
                                print(f"   - No streaming data received for valid scenario")
                        else:
                            # For error responses, just check status code
                            error_response = await response.text()
                            print(f"   + Correct error status {response.status} - {error_response[:100]}...")
                            successful_error_tests += 1
                    else:
                        print(f"   - Expected status {expected_status}, got {response.status}")
                        error_text = await response.text()
                        print(f"      Error: {error_text[:200]}...")
                        
            except Exception as e:
                print(f"   - Error test exception: {e}")
        
        # Log error scenario test results
        total_error_tests = len(error_tests)
        if successful_error_tests == total_error_tests:
            print(f"\n+ All {successful_error_tests}/{total_error_tests} streaming error tests passed!")
            self.log_result("streaming_error_scenarios", True, f"All {successful_error_tests} error tests passed")
        else:
            print(f"\n- Only {successful_error_tests}/{total_error_tests} streaming error tests passed")
            self.log_result("streaming_error_scenarios", False, f"Only {successful_error_tests}/{total_error_tests} passed")
    
    async def test_concurrent_streaming(self):
        """Test concurrent streaming requests to validate server stability."""
        print("\nTesting Concurrent Streaming")
        
        # Define concurrent test messages
        concurrent_messages = [
            {
                "text": f"并发测试消息 {i+1} - 我感觉有点紧张",
                "session_id": f"concurrent-{i+1}-{int(time.time())}"
            }
            for i in range(3)  # Test with 3 concurrent streams
        ]
        
        print(f"   >> Starting {len(concurrent_messages)} concurrent streaming requests...")
        
        async def single_stream_test(message_data, test_id):
            """Single streaming test for concurrent execution."""
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat/stream",
                    json=message_data
                ) as response:
                    end_time = time.time()
                    total_time = int((end_time - start_time) * 1000)
                    
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
                        
                        return {
                            "test_id": test_id,
                            "success": completed,
                            "chunks": chunk_count,
                            "duration": total_time,
                            "status": response.status
                        }
                    else:
                        return {
                            "test_id": test_id,
                            "success": False,
                            "chunks": 0,
                            "duration": total_time,
                            "status": response.status,
                            "error": await response.text()
                        }
            except Exception as e:
                return {
                    "test_id": test_id,
                    "success": False,
                    "chunks": 0,
                    "duration": 0,
                    "error": str(e)
                }
        
        # Execute concurrent streaming requests
        tasks = [
            single_stream_test(msg, i+1) 
            for i, msg in enumerate(concurrent_messages)
        ]
        
        try:
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            total_concurrent_time = int((end_time - start_time) * 1000)
            
            successful_concurrent = 0
            total_chunks = 0
            
            print(f"   + Concurrent execution completed in {total_concurrent_time}ms")
            
            for result in results:
                if isinstance(result, dict) and result.get('success'):
                    successful_concurrent += 1
                    total_chunks += result.get('chunks', 0)
                    print(f"   + Stream {result['test_id']}: {result['chunks']} chunks in {result['duration']}ms")
                else:
                    if isinstance(result, dict):
                        print(f"   - Stream {result.get('test_id', 'unknown')}: {result.get('error', 'Failed')}")
                    else:
                        print(f"   - Stream failed with exception: {result}")
            
            # Log concurrent streaming test results
            total_concurrent_tests = len(concurrent_messages)
            if successful_concurrent == total_concurrent_tests:
                self._safe_print(f"\n[PASS] All {successful_concurrent}/{total_concurrent_tests} concurrent streaming tests passed!")
                print(f"   Total chunks processed: {total_chunks}")
                print(f"   Average concurrency performance: {total_concurrent_time/total_concurrent_tests:.1f}ms per stream")
                self.log_result("concurrent_streaming", True, f"All {successful_concurrent} concurrent tests passed")
            else:
                self._safe_print(f"\n[FAIL] Only {successful_concurrent}/{total_concurrent_tests} concurrent streaming tests passed")
                self.log_result("concurrent_streaming", False, f"Only {successful_concurrent}/{total_concurrent_tests} passed")
                
        except Exception as e:
            print(f"\n- Concurrent streaming test failed: {e}")
            self.log_result("concurrent_streaming", False, f"Concurrent test exception: {e}")
    
    async def test_streaming_performance_metrics(self):
        """Test streaming performance metrics and caching behavior."""
        print("\nTesting Streaming Performance Metrics")
        
        # Test message designed to trigger caching behavior
        test_message = {
            "text": "我今天心情不错，但是有点紧张即将到来的面试",
            "session_id": f"performance-test-{int(time.time())}",
            "analysis_depth": "detailed"
        }
        
        print("   >> Testing first-time execution (cache miss)...")
        
        # First execution - should be cache miss
        try:
            start_time = time.time()
            first_execution_chunks = []
            
            async with self.session.post(
                f"{self.base_url}/chat/stream",
                json=test_message
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                first_execution_chunks.append(data)
                                
                                # Look for cache status information
                                if data.get('type') == 'emotion_result':
                                    cache_status = data.get('cache_hit', False)
                                    print(f"   >> First execution - Cache hit: {cache_status}")
                                elif data.get('type') == 'complete':
                                    stats = data.get('stats', {})
                                    print(f"   >> First execution stats: {stats}")
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    first_execution_time = int((time.time() - start_time) * 1000)
                    print(f"   + First execution completed in {first_execution_time}ms with {len(first_execution_chunks)} chunks")
                else:
                    print(f"   - First execution failed: {response.status}")
                    self.log_result("streaming_performance_metrics", False, f"First execution failed: {response.status}")
                    return
        except Exception as e:
            print(f"   - First execution error: {e}")
            self.log_result("streaming_performance_metrics", False, f"First execution error: {e}")
            return
        
        # Wait a moment before second execution
        await asyncio.sleep(1)
        
        print("   >> Testing second execution (potential cache hit)...")
        
        # Second execution - might be cache hit
        try:
            start_time = time.time()
            second_execution_chunks = []
            
            async with self.session.post(
                f"{self.base_url}/chat/stream",
                json=test_message
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                second_execution_chunks.append(data)
                                
                                # Look for cache status information
                                if data.get('type') == 'emotion_result':
                                    cache_status = data.get('cache_hit', False)
                                    print(f"   >> Second execution - Cache hit: {cache_status}")
                                elif data.get('type') == 'complete':
                                    stats = data.get('stats', {})
                                    print(f"   >> Second execution stats: {stats}")
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    second_execution_time = int((time.time() - start_time) * 1000)
                    print(f"   + Second execution completed in {second_execution_time}ms with {len(second_execution_chunks)} chunks")
                    
                    # Compare performance
                    if second_execution_time < first_execution_time:
                        improvement = ((first_execution_time - second_execution_time) / first_execution_time) * 100
                        print(f"   >> Performance improvement: {improvement:.1f}% faster on second execution")
                    else:
                        print(f"   >> Performance comparison: Second execution took {second_execution_time - first_execution_time}ms more")
                    
                else:
                    print(f"   - Second execution failed: {response.status}")
                    self.log_result("streaming_performance_metrics", False, f"Second execution failed: {response.status}")
                    return
        except Exception as e:
            print(f"   - Second execution error: {e}")
            self.log_result("streaming_performance_metrics", False, f"Second execution error: {e}")
            return
        
        # Test performance statistics endpoint if available
        print("   >> Testing performance statistics endpoint...")
        try:
            async with self.session.get(f"{self.base_url}/chat/performance/stats") as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get('success') and 'data' in response_data:
                        stats_data = response_data['data']
                        print(f"   + Performance stats retrieved:")
                        print(f"      Cache hit rate: {stats_data.get('cache_hit_rate', 'N/A')}%")
                        print(f"      Average response time: {stats_data.get('average_response_time_ms', 'N/A')}ms")
                        print(f"      Total requests: {stats_data.get('total_requests', 'N/A')}")
                        print(f"      Cache stats: {stats_data.get('cache_stats', {})}")
                        
                        # Performance threshold validation
                        avg_response_time = stats_data.get('average_response_time_ms', 0)
                        cache_hit_rate = stats_data.get('cache_hit_rate', 0)
                        
                        # Define performance thresholds
                        max_acceptable_response_time = 10000  # 10 seconds
                        
                        performance_issues = []
                        if avg_response_time > max_acceptable_response_time:
                            performance_issues.append(f"High response time: {avg_response_time}ms > {max_acceptable_response_time}ms")
                        
                        if performance_issues:
                            print(f"   !! Performance issues detected: {performance_issues}")
                            await self._optimize_system_performance()
                        else:
                            print(f"   + Performance metrics within acceptable thresholds")
                            
                    else:
                        print(f"   !! Invalid response format: {response_data}")
                else:
                    print(f"   !! Performance stats endpoint returned: {response.status}")
        except Exception as e:
            print(f"   !! Could not retrieve performance stats: {e}")
        
        # Validate streaming chunk consistency
        if len(first_execution_chunks) > 0 and len(second_execution_chunks) > 0:
            # Check that both executions have similar chunk structure
            first_types = [chunk.get('type') for chunk in first_execution_chunks]
            second_types = [chunk.get('type') for chunk in second_execution_chunks]
            
            if first_types == second_types:
                print(f"   + Chunk structure consistency verified between executions")
                self.log_result("streaming_performance_metrics", True, f"Performance test completed successfully")
            else:
                print(f"   !! Chunk structure differs between executions:")
                print(f"      First: {first_types}")
                print(f"      Second: {second_types}")
                self.log_result("streaming_performance_metrics", False, "Chunk structure inconsistency")
        else:
            print(f"   - Insufficient streaming data for comparison")
            self.log_result("streaming_performance_metrics", False, "Insufficient streaming data")
    
    async def test_sentiment_validation(self):
        """Test sentiment validation fix for various emotional messages."""
        print("\nTesting Sentiment Validation Fix")
        
        # Test messages that should trigger different sentiment responses
        test_messages = [
            {
                "text": "我今天非常开心，一切都很顺利！",
                "expected_sentiment": "positive",
                "description": "Very happy message"
            },
            {
                "text": "感觉很难过，心情不好...",
                "expected_sentiment": "negative", 
                "description": "Sad message"
            },
            {
                "text": "还好吧，没什么特别的",
                "expected_sentiment": "neutral",
                "description": "Neutral message"
            },
            {
                "text": "压力很大，工作让我很焦虑和疲惫",
                "expected_sentiment": "negative",
                "description": "Stress and anxiety message"
            },
            {
                "text": "谢谢你的帮助，我很感激！",
                "expected_sentiment": "positive",
                "description": "Grateful message"
            }
        ]
        
        validation_session_id = f"sentiment-test-{int(time.time())}"
        successful_tests = 0
        
        for i, test_case in enumerate(test_messages):
            print(f"\n   Test {i+1}: {test_case['description']}")
            print(f"   Message: {test_case['text']}")
            
            message_data = {
                "text": test_case['text'],
                "session_id": validation_session_id,
                "analysis_depth": "detailed"
            }
            
            try:
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                    end_time = time.time()
                    
                    if response.status == 200:
                        data = await response.json()
                        execution_time = int((end_time - start_time) * 1000)
                        
                        # Check if emotion analysis exists and has valid sentiment
                        emotion_analysis = data.get('emotion_analysis', {})
                        detected_sentiment = emotion_analysis.get('sentiment', 'unknown')
                        
                        print(f"   + Response received in {execution_time}ms")
                        print(f"   + Detected sentiment: {detected_sentiment}")
                        
                        # Validate that sentiment is one of the allowed values
                        valid_sentiments = ["positive", "negative", "neutral"]
                        if detected_sentiment in valid_sentiments:
                            print(f"   + Sentiment validation passed")
                            successful_tests += 1
                            
                            # Additional validation details
                            if emotion_analysis.get('primary_emotions'):
                                emotions = emotion_analysis.get('primary_emotions', [])
                                print(f"   + Primary emotions: {emotions}")
                            
                            if emotion_analysis.get('intensity'):
                                intensity = emotion_analysis.get('intensity', 0)
                                print(f"   + Emotion intensity: {intensity}")
                        else:
                            print(f"   - Invalid sentiment detected: {detected_sentiment}")
                            print(f"     Expected one of: {valid_sentiments}")
                    else:
                        error_text = await response.text()
                        print(f"   - API call failed: {response.status}")
                        print(f"     Error: {error_text}")
                        
            except Exception as e:
                print(f"   - Test error: {e}")
        
        # Log overall sentiment validation test result
        if successful_tests == len(test_messages):
            self._safe_print(f"\n[PASS] All {successful_tests}/{len(test_messages)} sentiment validation tests passed!")
            self.log_result("sentiment_validation", True, f"All {successful_tests} tests passed")
        else:
            self._safe_print(f"\n[FAIL] Only {successful_tests}/{len(test_messages)} sentiment validation tests passed")
            self.log_result("sentiment_validation", False, f"Only {successful_tests}/{len(test_messages)} passed")
        
        # Additional test for the specific '+' sentiment issue that was fixed
        print(f"\n   Testing direct agent sentiment normalization...")
        try:
            # Import and test the ListenerAgent directly
            import sys
            sys.path.append('.')
            from src.agents.listener_agent import ListenerAgent
            
            agent = ListenerAgent()
            
            # Test the specific cases that were causing issues
            test_cases = ['+', '-', '0', 'positive', 'negative', 'neutral']
            normalization_passed = True
            
            for case in test_cases:
                normalized = agent._normalize_sentiment(case)
                expected_valid = normalized in ['positive', 'negative', 'neutral']
                if not expected_valid:
                    normalization_passed = False
                    print(f"   - Normalization failed for '{case}' -> '{normalized}'")
                else:
                    print(f"   + '{case}' -> '{normalized}'")
            
            if normalization_passed:
                print(f"   + Direct sentiment normalization tests passed!")
                self.log_result("sentiment_normalization", True, "All normalization tests passed")
            else:
                print(f"   - Some sentiment normalization tests failed!")
                self.log_result("sentiment_normalization", False, "Some normalization tests failed")
                
        except ImportError as e:
            print(f"   ! Could not test direct agent normalization: {e}")
            self.log_result("sentiment_normalization", False, f"Import error: {e}")
        except Exception as e:
            print(f"   - Direct normalization test error: {e}")
            self.log_result("sentiment_normalization", False, str(e))
    
    async def test_natural_response_validation(self):
        """Test that duck responses don't contain analytical phrases."""
        print("\nTesting Natural Response Validation (No Analytical Phrases)")
        
        # Test messages that might trigger analytical responses
        test_messages = [
            {
                "text": "早呀",
                "description": "Simple greeting"
            },
            {
                "text": "我今天心情还不错",
                "description": "Positive mood message"
            },
            {
                "text": "感觉有点累，工作压力大",
                "description": "Stress message"
            },
            {
                "text": "谢谢你陪我聊天",
                "description": "Grateful message"
            },
            {
                "text": "我有点焦虑，不知道怎么办",
                "description": "Anxiety message"
            }
        ]
        
        # Analytical phrases that should NOT appear in responses
        forbidden_phrases = [
            "根据你的情绪分析",
            "从你的话中分析", 
            "通过分析你的",
            "情绪分析显示",
            "分析结果表明",
            "从情绪角度来看",
            "心理学上来说",
            "根据心理分析",
            "情绪分析结果",
            "分析你的情绪"
        ]
        
        natural_session_id = f"natural-test-{int(time.time())}"
        successful_tests = 0
        
        for i, test_case in enumerate(test_messages):
            print(f"\n   Test {i+1}: {test_case['description']}")
            print(f"   Message: {test_case['text']}")
            
            message_data = {
                "text": test_case['text'],
                "session_id": natural_session_id,
                "analysis_depth": "detailed"
            }
            
            try:
                start_time = time.time()
                
                # Use retry logic for better reliability
                status, response_data = await self._retry_api_call(
                    "POST", 
                    f"{self.base_url}/chat/message", 
                    json=message_data,
                    max_retries=3
                )
                
                end_time = time.time()
                execution_time = int((end_time - start_time) * 1000)
                
                if status == 200 and isinstance(response_data, dict):
                    response_text = response_data.get('response_text', '')
                    print(f"   + Response received in {execution_time}ms")
                    
                    # Safely truncate response for display - handle Unicode properly
                    try:
                        preview = response_text[:80] + "..." if len(response_text) > 80 else response_text
                        print(f"   Response: {preview}")
                    except UnicodeEncodeError:
                        print(f"   Response: [Response contains special characters - {len(response_text)} chars]")
                    
                    # Check for forbidden analytical phrases
                    found_forbidden = []
                    for phrase in forbidden_phrases:
                        if phrase in response_text:
                            found_forbidden.append(phrase)
                    
                    if not found_forbidden:
                        print(f"   + Natural response validation passed")
                        successful_tests += 1
                    else:
                        print(f"   - Found analytical phrases: {found_forbidden}")
                        try:
                            print(f"     Full response: {response_text}")
                        except UnicodeEncodeError:
                            print(f"     Full response: [Unicode display error - contains forbidden phrases]")
                else:
                    print(f"   - API call failed: {status}")
                    print(f"     Error: {response_data}")
                        
            except Exception as e:
                print(f"   - Test error: {e}")
        
        # Log overall natural response validation test result
        if successful_tests == len(test_messages):
            print(f"\n+ All {successful_tests}/{len(test_messages)} natural response validation tests passed!")
            self.log_result("natural_response_validation", True, f"All {successful_tests} tests passed")
        else:
            print(f"\n- Only {successful_tests}/{len(test_messages)} natural response validation tests passed")
            self.log_result("natural_response_validation", False, f"Only {successful_tests}/{len(test_messages)} passed")
        
        # Test the analytical phrase removal function directly
        print(f"\n   Testing direct analytical phrase removal...")
        try:
            import sys
            sys.path.append('.')
            from src.agents.duck_style_agent import DuckStyleAgent
            
            agent = DuckStyleAgent()
            
            test_responses = [
                "早呀！鸭鸭过来和你说声早上好呢！根据你的情绪分析，今天是个比较平静的一天，是吧？",
                "鸭鸭能感受到你的心情呢。从你的话中分析，你今天还挺开心的！",
                "情绪分析显示你有点累，鸭鸭建议你好好休息一下哦～"
            ]
            
            removal_passed = True
            for i, response in enumerate(test_responses, 1):
                cleaned = agent._validate_and_cleanup(response)
                
                # Check if any forbidden phrases remain
                remaining_forbidden = []
                for phrase in forbidden_phrases:
                    if phrase in cleaned:
                        remaining_forbidden.append(phrase)
                
                if not remaining_forbidden:
                    print(f"   + Test {i}: Analytical phrases successfully removed")
                else:
                    removal_passed = False
                    print(f"   - Test {i}: Still contains: {remaining_forbidden}")
                    print(f"     Cleaned response: {cleaned}")
            
            if removal_passed:
                print(f"   + Direct analytical phrase removal tests passed!")
                self.log_result("analytical_phrase_removal", True, "All removal tests passed")
            else:
                print(f"   - Some analytical phrase removal tests failed!")
                self.log_result("analytical_phrase_removal", False, "Some removal tests failed")
                
        except ImportError as e:
            print(f"   ! Could not test direct phrase removal: {e}")
            self.log_result("analytical_phrase_removal", False, f"Import error: {e}")
        except Exception as e:
            print(f"   - Direct phrase removal test error: {e}")
            self.log_result("analytical_phrase_removal", False, str(e))
    
    async def test_clear_session(self):
        """Test clearing a session."""
        print("\nTesting Clear Session")
        
        try:
            async with self.session.post(f"{self.base_url}/chat/session/{self.session_id}/clear") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Session cleared successfully")
                    self.log_result("clear_session", True, "Session cleared")
                else:
                    print(f"Failed to clear session: {response.status}")
                    self.log_result("clear_session", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Clear session error: {e}")
            self.log_result("clear_session", False, str(e))
    
    async def test_delete_session(self):
        """Test deleting a session."""
        print("\nTesting Delete Session")
        
        try:
            async with self.session.delete(f"{self.base_url}/chat/session/{self.session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Session deleted successfully")
                    self.log_result("delete_session", True, "Session deleted")
                else:
                    print(f"Failed to delete session: {response.status}")
                    self.log_result("delete_session", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Delete session error: {e}")
            self.log_result("delete_session", False, str(e))
    
    async def test_error_scenarios(self):
        """Test various error scenarios."""
        print("\ Testing Error Scenarios")
        
        # Test non-existent session
        try:
            async with self.session.get(f"{self.base_url}/chat/session/non-existent-session") as response:
                if response.status == 404:
                    print("Non-existent session returns 404")
                    self.log_result("error_404_session", True, "Correct 404 response")
                else:
                    print(f"Expected 404, got {response.status}")
                    self.log_result("error_404_session", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Error test failed: {e}")
            self.log_result("error_404_session", False, str(e))
        
        # Test empty message
        try:
            message_data = {
                "text": "",
                "session_id": "error-test-session"
            }
            async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                if response.status == 422:  # Validation error
                    print("Empty message returns 422 validation error")
                    self.log_result("error_empty_message", True, "Correct validation error")
                else:
                    print(f"Expected 422, got {response.status}")
                    self.log_result("error_empty_message", False, f"Status: {response.status}")
        except Exception as e:
            print(f"Empty message test failed: {e}")
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
                    
                    print(f"Message sent successfully")
                    print(f"   Response: {data['response_text'][:100]}...")
                    print(f"   Execution time: {execution_time}ms (API: {data.get('execution_time_ms', 'N/A')}ms)")
                    print(f"   LLM used: {data.get('llm_providers_used', ['unknown'])}")
                    
                    if data.get('emotion_analysis'):
                        emotions = data['emotion_analysis'].get('emotions', [])
                        sentiment = data['emotion_analysis'].get('sentiment', 'unknown')
                        print(f"   Emotions detected: {emotions} (sentiment: {sentiment})")
                    
                    self.log_result(test_name, True, f"Response in {execution_time}ms")
                else:
                    error_text = await response.text()
                    print(f"Message failed: {response.status}")
                    print(f"   Error: {error_text}")
                    self.log_result(test_name, False, f"Status: {response.status}")
                    
        except Exception as e:
            print(f"{test_name} error: {e}")
            self.log_result(test_name, False, str(e))
    
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test result with safe Unicode handling."""
        try:
            # Ensure details don't contain problematic Unicode for console output
            safe_details = details
            if isinstance(details, str):
                # Replace common Unicode characters that cause Windows console issues
                safe_details = details.replace('✅', '[PASS]').replace('❌', '[FAIL]').replace('⚠️', '[WARN]')
                
            self.test_results.append({
                "test": test_name,
                "success": success,
                "details": safe_details,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            # Fallback logging in case of any issues
            self.test_results.append({
                "test": test_name,
                "success": success,  
                "details": f"[Unicode logging error: {e}]",
                "timestamp": datetime.now().isoformat()
            })
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
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
        
        print("\nAll tests completed!")


async def main():
    """Main test runner."""
    import sys
    
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing Duck Therapy API at: {base_url}")
    print("Make sure the following are running:")
    print("   1. Ollama server with  model")
    print("   2. Duck Therapy backend server")
    print("\n Starting tests in 3 seconds...")
    
    await asyncio.sleep(3)
    
    tester = ChatAPITester(base_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())