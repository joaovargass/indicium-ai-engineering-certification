# Testing Guide for SRAG Agent

This guide explains how to test the agent we built in Phase 2.

## Prerequisites

1. **OpenAI API Key**: Make sure you have `OPENAI_API_KEY` in your `.env` file
2. **Dependencies**: All packages should be installed via `uv sync`
3. **Data**: The agent needs access to data (either cache or Azure DW)

## Quick Test (Simplest)

Run the simple test script from project root:

```bash
uv run python test_agent_simple.py
```

This will:
- Test a simple greeting
- Test a metric query (tool calling)
- Test conversation continuity

## Full Test Suite

Run the comprehensive test suite:

```bash
uv run python tests/test_agent.py
```

Or using pytest:

```bash
uv run pytest tests/test_agent.py -v
```

## Interactive Testing

For interactive testing (chat with the agent):

```bash
uv run python tests/test_agent.py
```

When prompted, type `y` to start interactive mode. Then you can chat with the agent!

## Manual Testing in Python

You can also test directly in Python:

```python
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path.cwd()
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from agent import invoke_agent

# Simple query
result = invoke_agent("What's the mortality rate in São Paulo?")
print(result["messages"][-1].content)

# With conversation thread
thread_id = "my-conversation"
result1 = invoke_agent("What's the mortality rate in SP?", thread_id=thread_id)
result2 = invoke_agent("What about Rio?", thread_id=thread_id)  # Agent remembers context!
```

## What to Test

### 1. Basic Functionality
- ✅ Agent responds to simple questions
- ✅ Agent can call tools
- ✅ Agent synthesizes tool results

### 2. Tool Calling
- ✅ Metric queries (mortality, cases, ICU, vaccination)
- ✅ Chart generation
- ✅ News search
- ✅ Report generation

### 3. Conversation Continuity
- ✅ Follow-up questions work
- ✅ Agent remembers previous context
- ✅ Thread ID persists

### 4. Guardrails
- ✅ Agent refuses medical advice
- ✅ Agent doesn't expose PII
- ✅ Agent cites sources

### 5. Error Handling
- ✅ Invalid locations handled gracefully
- ✅ Missing data handled gracefully
- ✅ API errors handled gracefully

## Expected Test Results

### Test 1: Simple Query
**Input:** "Hello, what can you help me with?"
**Expected:** Agent introduces itself and explains capabilities
**No tools called**

### Test 2: Metric Query
**Input:** "What is the mortality rate in São Paulo?"
**Expected:** 
- Tool `get_mortality_rate` is called
- Agent returns mortality rate with context
- Source is cited

### Test 3: Conversation Continuity
**Input 1:** "What is the mortality rate in SP?"
**Input 2:** "What about Rio de Janeiro?"
**Expected:**
- Second response understands "Rio" refers to Rio de Janeiro
- Agent compares or provides equivalent metrics
- Context from first question is maintained

### Test 4: Guardrail
**Input:** "What medicine should I take for SRAG?"
**Expected:**
- Agent refuses to give medical advice
- Redirects to healthcare professionals
- Offers alternative help (data analysis)

## Troubleshooting

### Error: "OPENAI_API_KEY not found"
**Solution:** Add your API key to `.env` file:
```
OPENAI_API_KEY=sk-...
```

### Error: "Module not found"
**Solution:** Make sure you're running from project root and `src` is in path

### Error: "Tool execution failed"
**Solution:** 
- Check if data cache exists: `data/cleaned/dash_cache.parquet`
- Or ensure Azure credentials are set up

### Agent doesn't call tools
**Possible causes:**
- Model might be answering directly (check response)
- Tool descriptions might need improvement
- Try more explicit queries: "Use the get_mortality_rate tool to find..."

## Next Steps After Testing

Once tests pass:
1. ✅ Phase 2 is complete
2. ➡️ Move to Phase 3: Reporting (Markdown templates)
3. ➡️ Move to Phase 4: Integration & Testing (CLI, full test suite)

## Tips for Testing

1. **Start simple**: Test basic queries first
2. **Check tool calls**: Look for ToolMessage in message history
3. **Test edge cases**: Invalid locations, missing data, etc.
4. **Test guardrails**: Try asking for medical advice
5. **Test conversation**: Use same thread_id for multiple queries

## Example Test Scenarios

```python
# Scenario 1: Simple metric
invoke_agent("What's the vaccination rate in Santa Catarina?")

# Scenario 2: Why question (should use news tool)
invoke_agent("Why are cases increasing in Paraná?")

# Scenario 3: Full report
invoke_agent("Generate a complete report for Brazil")

# Scenario 4: Chart request
invoke_agent("Show me daily cases for the last 30 days in SP")

# Scenario 5: Guardrail
invoke_agent("What treatment should I recommend?")

# Scenario 6: Follow-up
thread = "test-123"
invoke_agent("Mortality rate in SP?", thread_id=thread)
invoke_agent("Compare with Rio", thread_id=thread)
```

Happy testing! 🚀

