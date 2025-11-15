"""
Simple test script for the MAD API.
"""

import asyncio
import httpx


async def test_api():
    """Test the MAD API endpoints."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("Testing MAD API")
        print("=" * 60)

        # Test 1: Root endpoint
        print("\n1. Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        # Test 2: List posters
        print("2. Testing /posters endpoint...")
        response = await client.get(f"{base_url}/posters")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Found {data['count']} posters")
        for poster in data['posters'][:2]:  # Show first 2
            print(f"  - {poster['title']} ({poster['id']})")
        print()

        # Test 3: Get specific poster
        print("3. Testing /posters/poster_001 endpoint...")
        response = await client.get(f"{base_url}/posters/poster_001")
        poster = response.json()
        print(f"Status: {response.status_code}")
        print(f"Title: {poster['title']}")
        print(f"Authors: {', '.join(poster['authors'])}")
        print()

        # Test 4: Guide agent
        print("4. Testing guide agent...")
        response = await client.post(
            f"{base_url}/agent",
            json={
                "agent_type": "guide",
                "message": "Hello! What posters do you have about robotics?"
            }
        )
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Agent: {data['agent_type']}")
        print(f"Reply: {data['reply']}\n")

        # Test 5: Poster host agent
        print("5. Testing poster host agent...")
        response = await client.post(
            f"{base_url}/agent",
            json={
                "agent_type": "poster_host",
                "message": "What is this research about?",
                "poster_id": "poster_001"
            }
        )
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Agent: {data['agent_type']}")
        print(f"Poster: {data['poster_id']}")
        print(f"Reply: {data['reply']}\n")

        # Test 6: Health check
        print("6. Testing /health endpoint...")
        response = await client.get(f"{base_url}/health")
        health = response.json()
        print(f"Status: {response.status_code}")
        print(f"Health: {health}\n")

        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api())
