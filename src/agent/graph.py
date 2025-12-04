"""
LangGraph StateGraph implementation for SRAG agent.

Creates an execution graph that receives user messages, decides tool usage,
executes tools, and generates responses while maintaining conversation history.
"""

import uuid
from typing import Annotated, Callable, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.prompts import SYSTEM_PROMPT
from tools import ALL_TOOLS

load_dotenv()


class AgentState(TypedDict):
    """State schema for the agent graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str


def create_agent_node(llm: ChatOpenAI) -> Callable[[AgentState], AgentState]:
    """
    Create the agent node function that processes user input.

    Args:
        llm: ChatOpenAI instance

    Returns:
        Function that takes state and returns updated state

    """
    agent_runnable = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState) -> AgentState:
        """Process messages and decide on tool usage."""
        messages = state["messages"]

        has_system = any(isinstance(msg, SystemMessage) for msg in messages)
        if not has_system:
            messages_with_system = [SystemMessage(content=SYSTEM_PROMPT), *messages]
        else:
            messages_with_system = messages

        response = agent_runnable.invoke(messages_with_system)
        return {"messages": [response]}

    return agent_node


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Route to tools node if tool calls present, otherwise end.

    Args:
        state: Current graph state

    Returns:
        "tools" if tool calls needed, "end" otherwise

    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


def create_agent_graph(
    model_name: str = "gpt-5-nano",
    temperature: float = 0.0,
) -> StateGraph:
    """
    Create and compile the SRAG agent graph.

    Args:
        model_name: OpenAI model to use
        temperature: LLM temperature (0 = deterministic)

    Returns:
        Compiled StateGraph ready to use

    """
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    agent = create_agent_node(llm)
    tools = ToolNode(ALL_TOOLS)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent)
    workflow.add_node("tools", tools)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )
    workflow.add_edge("tools", "agent")

    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    return app


def invoke_agent(
    message: str,
    thread_id: str | None = None,
    model_name: str = "gpt-5-nano",
    temperature: float = 0.0,
) -> dict:
    """
    Invoke the agent with a user message.

    Args:
        message: User's message/question
        thread_id: Conversation thread ID (auto-generated if None)
        model_name: OpenAI model to use
        temperature: LLM temperature

    Returns:
        Dictionary with messages and thread_id

    """
    graph = create_agent_graph(model_name=model_name, temperature=temperature)

    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)], "thread_id": thread_id},
        config=config,
    )

    return result
