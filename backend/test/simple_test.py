"""
Simple API Test for Duck Therapy Chat API
Tests basic functionality without Unicode issues on Windows.
"""
import asyncio
import aiohttp
import json


async def test_basic_api():
    """Test basic API functionality."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("Testing Duck Therapy Chat API")
        print("=" * 40)
        
        # Test health check
        print("\n1. Testing Health Check")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   SUCCESS: {data}")
                else:
                    print(f"   FAILED: Status {response.status}")
                    return False
        except Exception as e:
            print(f"   ERROR: Cannot connect to server - {e}")
            print("   Make sure server is running: python start.py")
            return False
        
        # Test chat message
        print("\n2. Testing Chat Message")
        try:
            message_data = {
                "text": "你好鸭鸭，我今天感觉很好！",
                "session_id": "simple-test-session"
            }
            
            async with session.post(
                f"{base_url}/chat/message",
                json=message_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   SUCCESS: Response received")
                    print(f"   Response text: {data.get('response_text', 'No response')[:100]}...")
                    print(f"   Execution time: {data.get('execution_time_ms')}ms")
                    print(f"   LLM used: {data.get('llm_providers_used')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"   FAILED: Status {response.status}")
                    print(f"   Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"   ERROR: {e}")
            return False


async def main():
    """Run the simple test."""
    success = await test_basic_api()
    
    print("\n" + "=" * 40)
    if success:
        print("SUCCESS: Basic API test passed!")
        print("\nThe Duck Therapy API is working correctly.")
        print("You can now:")
        print("1. Use the Python test suite: python test_chat_api.py")
        print("2. Use cURL commands: ./test_commands.sh") 
        print("3. Import Postman collection for GUI testing")
    else:
        print("FAILED: API test failed!")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is running: ollama run qwen2.5")
        print("2. Make sure backend is running: python start.py")
        print("3. Check server logs for detailed errors")


if __name__ == "__main__":
    asyncio.run(main())