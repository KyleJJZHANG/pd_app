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
        print("Duck Therapy Chat API Test Suite")
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
            await self.test_streaming_error_scenarios()
            await self.test_concurrent_streaming()
            await self.test_streaming_performance_metrics()
            await self.test_sentiment_validation()
            await self.test_natural_response_validation()
            await self.test_clear_session()
            await self.test_delete_session()
            await self.test_error_scenarios()
            
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
            print(f"\n+ All {successful_streaming_tests}/{total_streaming_tests} streaming tests passed!")
            self.log_result("streaming_message", True, f"All {successful_streaming_tests} tests passed")
        else:
            print(f"\n- Only {successful_streaming_tests}/{total_streaming_tests} streaming tests passed")
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
                    "text": "测试" * 10000,  # Very long message
                    "session_id": f"long-stream-{int(time.time())}"
                },
                "expected_status": 200,  # Should handle gracefully
                "description": "Very long message streaming test"
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
                print(f"\n+ All {successful_concurrent}/{total_concurrent_tests} concurrent streaming tests passed!")
                print(f"   Total chunks processed: {total_chunks}")
                print(f"   Average concurrency performance: {total_concurrent_time/total_concurrent_tests:.1f}ms per stream")
                self.log_result("concurrent_streaming", True, f"All {successful_concurrent} concurrent tests passed")
            else:
                print(f"\n- Only {successful_concurrent}/{total_concurrent_tests} concurrent streaming tests passed")
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
                    stats_data = await response.json()
                    print(f"   + Performance stats retrieved:")
                    print(f"      Cache hit rate: {stats_data.get('cache_hit_rate', 'N/A')}%")
                    print(f"      Average response time: {stats_data.get('average_response_time', 'N/A')}ms")
                    print(f"      Total requests: {stats_data.get('total_requests', 'N/A')}")
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
            print(f"\n+ All {successful_tests}/{len(test_messages)} sentiment validation tests passed!")
            self.log_result("sentiment_validation", True, f"All {successful_tests} tests passed")
        else:
            print(f"\n- Only {successful_tests}/{len(test_messages)} sentiment validation tests passed")
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
                async with self.session.post(f"{self.base_url}/chat/message", json=message_data) as response:
                    end_time = time.time()
                    
                    if response.status == 200:
                        data = await response.json()
                        execution_time = int((end_time - start_time) * 1000)
                        
                        response_text = data.get('response_text', '')
                        print(f"   + Response received in {execution_time}ms")
                        print(f"   Response: {response_text[:80]}...")
                        
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
                            print(f"     Full response: {response_text}")
                    else:
                        error_text = await response.text()
                        print(f"   - API call failed: {response.status}")
                        print(f"     Error: {error_text}")
                        
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