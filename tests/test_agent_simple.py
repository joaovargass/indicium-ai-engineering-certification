"""
Simple test script for SRAG agent - Quick start guide.

Run this from project root:
    uv run python tests/test_agent_simple.py
"""

import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from agent import invoke_agent


def main():
    """Run a simple test by asking the agent a question."""
    print("=" * 60)
    print("SRAG AGENT - SIMPLE TEST")
    print("=" * 60)
    print()

    # Test 1: Simple greeting
    print("Test 1: Simple greeting")
    print("-" * 60)
    try:
        result = invoke_agent("Hello, what can you help me with?")
        response = result["messages"][-1].content
        print(f"Agent: {response[:200]}...")
        print("✅ Test 1 passed!\n")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}\n")

    # Test 2: Metric query
    print("Test 2: Metric query (requires tool)")
    print("-" * 60)
    try:
        result = invoke_agent("What is the mortality rate in São Paulo?")
        response = result["messages"][-1].content
        print(f"Agent: {response[:300]}...")
        print("✅ Test 2 passed!\n")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}\n")

    # Test 3: Follow-up question
    print("Test 3: Follow-up question (conversation continuity)")
    print("-" * 60)
    thread_id = "test-123"
    try:
        # First question
        result1 = invoke_agent("What is the mortality rate in SP?", thread_id=thread_id)
        print(f"First response: {result1['messages'][-1].content[:100]}...")

        # Follow-up
        result2 = invoke_agent("What about Rio de Janeiro?", thread_id=thread_id)
        print(f"Follow-up response: {result2['messages'][-1].content[:200]}...")
        print("✅ Test 3 passed!\n")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}\n")

    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
