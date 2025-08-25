"""
Simple streaming test for Duck Therapy API
Tests only the core streaming functionality without Unicode issues
"""
import asyncio
import aiohttp
import json
import time


async def test_streaming():
    """Test streaming functionality with basic cases."""
    print("Testing Duck Therapy Streaming API")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "name": "Basic Streaming",
            "data": {
                "text": "Hello duck",
                "session_id": f"stream-test-{int(time.time())}"
            }
        },
        {
            "name": "Empty Message (Should fail with 422)",
            "data": {
                "text": "",
                "session_id": f"empty-test-{int(time.time())}"
            }
        },
        {
            "name": "Long Message",
            "data": {
                "text": "This is a long test message to see if streaming handles longer content properly without any issues",
                "session_id": f"long-test-{int(time.time())}"
            }
        }
    ]
    
    successful_tests = 0
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")
            
            try:
                start_time = time.time()
                
                async with session.post(
                    f"{base_url}/chat/stream",
                    json=test_case['data']
                ) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status in [200, 422]:  # Expected statuses
                        if response.status == 422:
                            # This is expected for empty message
                            error_text = await response.text()
                            print(f"   Expected validation error: {error_text[:100]}")
                            successful_tests += 1
                            continue
                        
                        # Process streaming response
                        chunk_count = 0
                        chunk_types = []
                        received_complete = False
                        
                        async for line in response.content:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                chunk_count += 1
                                data_str = line_str[6:]  # Remove 'data: ' prefix
                                
                                try:
                                    data = json.loads(data_str)
                                    chunk_type = data.get('type', 'unknown')
                                    chunk_types.append(chunk_type)
                                    
                                    print(f"   Chunk {chunk_count}: {chunk_type}")
                                    
                                    if chunk_type == 'complete':
                                        received_complete = True
                                        stats = data.get('stats', {})
                                        total_time_ms = data.get('total_time_ms', 0)
                                        print(f"   Completed in {total_time_ms}ms")
                                        break
                                    elif chunk_type == 'error':
                                        print(f"   Error: {data.get('message', 'Unknown error')}")
                                        break
                                        
                                except json.JSONDecodeError as e:
                                    print(f"   JSON decode error: {e}")
                                    continue
                        
                        # Validate completeness
                        expected_types = ['emotion_start', 'emotion_result', 'response_start', 'response_end', 'complete']
                        missing_types = [t for t in expected_types if t not in chunk_types]
                        
                        if received_complete and not missing_types:
                            print(f"   SUCCESS: Complete streaming workflow")
                            successful_tests += 1
                        else:
                            print(f"   INCOMPLETE: Missing {missing_types}")
                    else:
                        error_text = await response.text()
                        print(f"   FAILED: Status {response.status}, Error: {error_text[:100]}")
                        
            except Exception as e:
                print(f"   EXCEPTION: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"RESULTS: {successful_tests}/{len(test_cases)} tests passed")
    
    if successful_tests == len(test_cases):
        print("All streaming tests passed!")
        return True
    else:
        print("Some streaming tests failed")
        return False


async def main():
    success = await test_streaming()
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)