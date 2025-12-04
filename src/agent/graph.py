"""LangGraph StateGraph implementation for SRAG agent.

This module creates the agent's execution graph that:
1. Receives user messages
2. Decides which tools to use (or answers directly)
3. Executes tools and processes results
4. Generates natural language responses
5. Maintains conversation history

The graph is extensible - new tools can be added to src.tools.ALL_TOOLS
and will automatically be available to the agent.
"""

import uuid
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.prompts import SYSTEM_PROMPT
from tools import ALL_TOOLS

# Load environment variables (for OpenAI API key)
load_dotenv()


# ============================================================================
# STEP 1: Define Agent State
# ============================================================================
# This TypedDict defines what data flows through the graph.
# - messages: List of all conversation messages (user, agent, tool responses)
# - thread_id: Unique ID for this conversation (enables memory/context)
# ============================================================================

class AgentState(TypedDict):
    """State schema for the agent graph.
    
    Attributes:
        messages: List of conversation messages (HumanMessage, AIMessage, ToolMessage)
        thread_id: Unique conversation identifier for memory persistence
    """
    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str


# ============================================================================
# STEP 2: Create Agent Node Function
# ============================================================================
# This function is the "brain" of the agent. It:
# 1. Receives the current state (with conversation history)
# 2. Creates an LLM instance with all tools bound
# 3. Invokes the LLM with system prompt + messages
# 4. Returns updated state with new AI message (and possibly tool calls)
# ============================================================================

def create_agent_node(llm: ChatOpenAI):
    """Create the agent node function that processes user input.
    
    Args:
        llm: ChatOpenAI instance with tools bound
        
    Returns:
        Function that takes state and returns updated state
    """
    # Bind all tools to the LLM - this makes tools available to the agent
    # The LLM will decide when to call which tool based on user queries
    agent_runnable = llm.bind_tools(ALL_TOOLS)
    
    def agent_node(state: AgentState) -> AgentState:
        """Agent node: processes messages and decides on tool usage.
        
        Args:
            state: Current graph state with messages and thread_id
            
        Returns:
            Updated state with new AI message (may include tool calls)
        """
        # Get the current messages from state
        messages = state["messages"]
        
        # Create a list with system prompt + conversation history
        # System prompt is prepended to guide agent behavior
        # Check if system message already exists (to avoid duplicates)
        has_system = any(isinstance(msg, SystemMessage) for msg in messages)
        if not has_system:
            messages_with_system = [SystemMessage(content=SYSTEM_PROMPT), *messages]
        else:
            messages_with_system = messages
        
        # Invoke the LLM with messages
        # The LLM will either:
        # - Answer directly (no tool calls)
        # - Request tool calls (tool_calls in response)
        response = agent_runnable.invoke(messages_with_system)
        
        # Return updated state with new AI message
        return {"messages": [response]}
    
    return agent_node


# ============================================================================
# STEP 3: Create Conditional Router Function
# ============================================================================
# This function decides the next step in the graph:
# - If the agent's response has tool calls → route to "tools" node
# - If no tool calls → route to "end" (ready to respond to user)
# ============================================================================

def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Conditional router: decides whether to call tools or end.
    
    Args:
        state: Current graph state
        
    Returns:
        "tools" if tool calls are needed, "end" if ready to respond
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if the last message has tool calls
    # Tool calls indicate the agent wants to use a tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    else:
        return "end"


# ============================================================================
# STEP 4: Build and Compile the Graph
# ============================================================================
# This function creates the complete graph:
# 1. Create StateGraph with AgentState schema
# 2. Add nodes: "agent" (thinks) and "tools" (executes tools)
# 3. Add edges: agent → router → tools/end, tools → agent (loop)
# 4. Add checkpointer for conversation memory
# 5. Compile and return runnable graph
# ============================================================================

def create_agent_graph(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.0,
) -> StateGraph:
    """Create and compile the SRAG agent graph.
    
    This function builds the complete agent workflow:
    - User message → Agent node → Router → Tools (if needed) → Agent → End
    
    Args:
        model_name: OpenAI model to use (default: gpt-4o-mini, fallback if gpt-5-nano unavailable)
        temperature: LLM temperature (0 = deterministic, good for data analysis)
        
    Returns:
        Compiled StateGraph ready to use
        
    Example:
        graph = create_agent_graph()
        result = graph.invoke(
            {"messages": [HumanMessage("What's the mortality rate in SP?")], "thread_id": "abc123"}
        )
    """
    # Create LLM instance
    # Temperature 0 ensures deterministic, consistent responses for data analysis
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    
    # Create agent node function (with LLM and tools bound)
    agent = create_agent_node(llm)
    
    # Create tool node - this executes tool calls
    # ToolNode is a pre-built LangGraph node that:
    # - Takes tool calls from agent
    # - Executes the appropriate tool
    # - Returns ToolMessage with results
    tools = ToolNode(ALL_TOOLS)
    
    # Create the state graph with our state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    # Node 1: "agent" - processes messages, decides on tool usage
    workflow.add_node("agent", agent)
    
    # Node 2: "tools" - executes tool calls
    workflow.add_node("tools", tools)
    
    # Set entry point: graph starts at "agent" node
    workflow.set_entry_point("agent")
    
    # Add conditional edge: agent → router → tools or end
    # This checks if tool calls are needed
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # If tools needed, go to tools node
            "end": END,        # If no tools, end and return to user
        },
    )
    
    # Add edge: tools → agent (loop back)
    # After tools execute, return to agent to synthesize results
    workflow.add_edge("tools", "agent")
    
    # Create checkpointer for conversation memory
    # MemorySaver stores conversation history per thread_id
    # This enables follow-up questions and context retention
    checkpointer = MemorySaver()
    
    # Compile the graph with checkpointer
    # This creates a runnable graph that can process conversations
    app = workflow.compile(checkpointer=checkpointer)
    
    return app


# ============================================================================
# STEP 5: Helper Function for Easy Usage
# ============================================================================
# This function makes it easy to invoke the agent with a simple message
# ============================================================================

def invoke_agent(
    message: str,
    thread_id: str | None = None,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.0,
) -> dict:
    """Invoke the agent with a user message.
    
    This is a convenience function that:
    1. Creates the graph
    2. Generates a thread_id if not provided
    3. Invokes the graph with the message
    4. Returns the result
    
    Args:
        message: User's message/question
        thread_id: Conversation thread ID (auto-generated if None)
        model_name: OpenAI model to use
        temperature: LLM temperature
        
    Returns:
        Dictionary with messages and thread_id
        
    Example:
        result = invoke_agent("What's the mortality rate in São Paulo?")
        print(result["messages"][-1].content)
    """
    # Create the graph
    graph = create_agent_graph(model_name=model_name, temperature=temperature)
    
    # Generate thread_id if not provided
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    # Create config for this conversation thread
    config = {"configurable": {"thread_id": thread_id}}
    
    # Invoke the graph with user message
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)], "thread_id": thread_id},
        config=config,
    )
    
    return result

