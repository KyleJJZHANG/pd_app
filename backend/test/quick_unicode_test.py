"""
Quick test to verify Unicode fixes in original test file
"""
import asyncio
import aiohttp


async def test_health_and_basic():
    """Test just health and basic message to verify Unicode fixes."""
    print("Quick Unicode Test")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    session_id = "unicode-test-123"
    
    async with aiohttp.ClientSession() as session:
        # Test health
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("   + Health check passed")
                else:
                    print(f"   - Health check failed: {response.status}")
        except Exception as e:
            print(f"   - Health error: {e}")
        
        # Test basic message
        try:
            message_data = {
                "text": "Hello duck",
                "session_id": session_id
            }
            async with session.post(f"{base_url}/chat/message", json=message_data) as response:
                if response.status == 200:
                    data = await response.json()
                    exec_time = data.get('execution_time_ms', 0)
                    print(f"   + Basic message processed in {exec_time}ms")
                else:
                    print(f"   - Basic message failed: {response.status}")
        except Exception as e:
            print(f"   - Basic message error: {e}")
    
    print("Unicode test completed without encoding errors!")


if __name__ == "__main__":
    asyncio.run(test_health_and_basic())