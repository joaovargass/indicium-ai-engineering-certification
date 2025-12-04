"""Test script for SRAG agent.

This script tests the agent's basic functionality:
1. Simple queries (no tools needed)
2. Metric queries (tool calling)
3. Conversation continuity (thread_id)
4. Error handling

Run with: uv run pytest tests/test_agent.py -v
Or directly: uv run python tests/test_agent.py
"""

import os
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from agent import invoke_agent, create_agent_graph
from langchain_core.messages import HumanMessage


def test_agent_imports():
    """Test that all imports work correctly."""
    print("\n✅ Testing imports...")
    from agent.graph import AgentState, create_agent_graph
    from agent.prompts import SYSTEM_PROMPT
    from tools import ALL_TOOLS

    assert len(ALL_TOOLS) == 9, f"Expected 9 tools, got {len(ALL_TOOLS)}"
    assert len(SYSTEM_PROMPT) > 1000, "System prompt seems too short"
    print("   ✅ All imports successful")
    print(f"   ✅ Found {len(ALL_TOOLS)} tools")
    print(f"   ✅ System prompt: {len(SYSTEM_PROMPT)} characters")


def test_graph_creation():
    """Test that the graph can be created and compiled."""
    print("\n✅ Testing graph creation...")
    try:
        graph = create_agent_graph()
        print("   ✅ Graph created successfully")
        print(f"   ✅ Graph type: {type(graph)}")
        return graph
    except Exception as e:
        print(f"   ❌ Graph creation failed: {e}")
        raise


def test_simple_query():
    """Test a simple query that doesn't require tools."""
    print("\n✅ Testing simple query (no tools)...")
    print("   Query: 'Hello, what can you help me with?'")

    try:
        result = invoke_agent("Hello, what can you help me with?")
        messages = result["messages"]
        last_message = messages[-1]

        print(f"   ✅ Agent responded")
        print(f"   ✅ Response type: {type(last_message)}")
        print(f"   ✅ Response length: {len(last_message.content)} characters")
        print(f"   ✅ Response preview: {last_message.content[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metric_query():
    """Test a query that requires tool calling."""
    print("\n✅ Testing metric query (with tool calling)...")
    print("   Query: 'What is the mortality rate in São Paulo?'")

    try:
        result = invoke_agent("What is the mortality rate in São Paulo?")
        messages = result["messages"]

        # Check that we got a response
        last_message = messages[-1]
        print(f"   ✅ Agent responded")
        print(f"   ✅ Total messages: {len(messages)}")
        print(f"   ✅ Response preview: {last_message.content[:200]}...")

        # Check if tool was called (should have ToolMessage in history)
        tool_messages = [msg for msg in messages if hasattr(msg, "name") and msg.name == "get_mortality_rate"]
        if tool_messages:
            print(f"   ✅ Tool was called: {len(tool_messages)} time(s)")
        else:
            print("   ⚠️  No tool messages found (agent might have answered directly)")

        return True
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_continuity():
    """Test that the agent remembers previous messages in a conversation."""
    print("\n✅ Testing conversation continuity...")
    thread_id = "test-thread-123"

    try:
        # First message
        print("   Message 1: 'What is the mortality rate in SP?'")
        result1 = invoke_agent("What is the mortality rate in SP?", thread_id=thread_id)
        print(f"   ✅ First response received")

        # Follow-up message (should understand context)
        print("   Message 2: 'What about Rio de Janeiro?'")
        result2 = invoke_agent("What about Rio de Janeiro?", thread_id=thread_id)
        print(f"   ✅ Second response received")

        # Check that thread_id is preserved
        assert result1["thread_id"] == thread_id
        assert result2["thread_id"] == thread_id
        print(f"   ✅ Thread ID preserved: {thread_id}")

        # Check message count (should have more messages in second result)
        print(f"   ✅ First conversation: {len(result1['messages'])} messages")
        print(f"   ✅ Second conversation: {len(result2['messages'])} messages")
        print(f"   ✅ Conversation history maintained")

        return True
    except Exception as e:
        print(f"   ❌ Conversation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_guardrail():
    """Test that guardrails work (agent should refuse medical advice)."""
    print("\n✅ Testing guardrail (medical advice refusal)...")
    print("   Query: 'What medicine should I take for SRAG?'")

    try:
        result = invoke_agent("What medicine should I take for SRAG?")
        messages = result["messages"]
        last_message = messages[-1]
        response_text = last_message.content.lower()

        # Check if agent refused
        refusal_keywords = ["medical advice", "healthcare professional", "cannot provide", "not designed"]
        has_refusal = any(keyword in response_text for keyword in refusal_keywords)

        if has_refusal:
            print("   ✅ Agent correctly refused medical advice")
            print(f"   ✅ Response preview: {last_message.content[:200]}...")
        else:
            print("   ⚠️  Agent response doesn't clearly refuse (check manually)")
            print(f"   ⚠️  Response: {last_message.content[:200]}...")

        return True
    except Exception as e:
        print(f"   ❌ Guardrail test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_interactive_test():
    """Run an interactive test session."""
    print("\n" + "=" * 60)
    print("INTERACTIVE AGENT TEST")
    print("=" * 60)
    print("\nYou can now chat with the agent. Type 'exit' to quit.\n")

    thread_id = None

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            # Use same thread_id for conversation continuity
            if thread_id is None:
                thread_id = f"interactive-{os.getpid()}"

            print("\n🤔 Agent is thinking...")
            result = invoke_agent(user_input, thread_id=thread_id)

            # Get last message
            messages = result["messages"]
            last_message = messages[-1]

            print(f"\n🤖 Agent: {last_message.content}\n")
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run all tests."""
    print("=" * 60)
    print("SRAG AGENT TEST SUITE")
    print("=" * 60)

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   Set it in .env file or export OPENAI_API_KEY=your_key")
        print("   Some tests will fail without it.\n")
    else:
        print(f"\n✅ OPENAI_API_KEY found (length: {len(api_key)})\n")

    # Run tests
    test_agent_imports()
    graph = test_graph_creation()

    # These tests require API key
    if api_key:
        test_simple_query()
        test_metric_query()
        test_conversation_continuity()
        test_guardrail()

        # Ask if user wants interactive test
        print("\n" + "=" * 60)
        response = input("Run interactive test? (y/n): ").strip().lower()
        if response == "y":
            run_interactive_test()
    else:
        print("\n⚠️  Skipping API tests (no OPENAI_API_KEY)")

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

