"""
LangGraph StateGraph implementation for SRAG agent.

Creates an execution graph that receives user messages, decides tool usage,
executes tools, and generates responses while maintaining conversation history.
"""

import time
import uuid
from typing import Annotated, Callable, Literal, TypedDict

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.prompts import SYSTEM_PROMPT
from common.config import (
    AGENT_TOOL_RESULT_DELAY_SECONDS,
    AGENT_TOOL_STEP_DELAY_SECONDS,
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    TOOL_STEP_MAPPING,
)
from common.logging import logger
from tools import ALL_TOOLS


class AgentState(TypedDict):
    """State schema for the agent graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str


def _to_langchain_messages(ui_messages: list[dict]) -> list[BaseMessage]:
    """
    Convert UI message format to LangChain message objects.

    Args:
        ui_messages: List of message dicts with "role" and "content" keys

    Returns:
        List of LangChain BaseMessage objects

    """
    langchain_messages = []
    for msg in ui_messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")

        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))
        elif role == "system":
            langchain_messages.append(SystemMessage(content=content))

    return langchain_messages


def _build_messages_list(
    conversation_history: list[BaseMessage] | None, message: str
) -> list[BaseMessage]:
    """Build messages list from history and current user message."""
    messages_list = []
    if conversation_history:
        messages_list.extend(conversation_history)
    messages_list.append(HumanMessage(content=message))
    return messages_list


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


def _extract_tool_call_info(tool_call: dict | object) -> tuple[str, str, dict]:
    """
    Extract tool name, id, and args from a tool call.

    Args:
        tool_call: Tool call as dict or Pydantic ToolCall object

    Returns:
        Tuple of (tool_name, tool_id, tool_args)

    """
    if isinstance(tool_call, dict):
        return (
            tool_call.get("name", ""),
            tool_call.get("id", ""),
            tool_call.get("args", {}),
        )
    return (
        getattr(tool_call, "name", ""),
        getattr(tool_call, "id", ""),
        getattr(tool_call, "args", {}),
    )


def _execute_tool(tool: object, tool_args: dict, tool_id: str) -> ToolMessage:
    """
    Execute a single tool and return the result as a ToolMessage.

    Args:
        tool: The tool to execute
        tool_args: Arguments to pass to the tool
        tool_id: Tool call ID for the response message

    Returns:
        ToolMessage with result or error content

    """
    try:
        result = tool.invoke(tool_args)
        if isinstance(result, dict):
            import json

            content = json.dumps(result, ensure_ascii=False)
        else:
            content = str(result)
        return ToolMessage(content=content, tool_call_id=tool_id)
    except (ValueError, KeyError, TypeError) as e:
        return ToolMessage(content=f"Erro: {e}", tool_call_id=tool_id)
    except Exception as e:
        return ToolMessage(content=f"Erro: {e}", tool_call_id=tool_id)


def create_tool_node(
    tools: list, step_callback: Callable[[str], None] | None = None
) -> Callable[[AgentState], AgentState]:
    """
    Create a sequential tool node that executes tools one by one with step callbacks.

    Args:
        tools: List of tools to execute
        step_callback: Optional callback function called before each tool execution

    Returns:
        Function that takes state and returns updated state with tool results

    """
    tool_dict = {tool.name: tool for tool in tools}

    def sequential_tool_node(state: AgentState) -> AgentState:
        """Execute tools sequentially, updating callback for each."""
        messages = state["messages"]
        last_message = messages[-1]

        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"messages": []}

        tool_messages = []

        for tool_call in last_message.tool_calls:
            tool_name, tool_id, tool_args = _extract_tool_call_info(tool_call)

            if step_callback:
                step_message = TOOL_STEP_MAPPING.get(
                    tool_name, f"Executando {tool_name}..."
                )
                step_callback(step_message)
                time.sleep(AGENT_TOOL_STEP_DELAY_SECONDS)

            if tool_name in tool_dict:
                tool_message = _execute_tool(tool_dict[tool_name], tool_args, tool_id)
                tool_messages.append(tool_message)

        if step_callback and tool_messages:
            step_callback("Processando resultados...")
            time.sleep(AGENT_TOOL_RESULT_DELAY_SECONDS)

        return {"messages": tool_messages}

    return sequential_tool_node


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Route to tools node if agent has tool calls, otherwise end."""
    messages = state["messages"]
    if not messages:
        return "end"

    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"


def create_agent_graph(
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: float = DEFAULT_TEMPERATURE,
    use_checkpointer: bool = False,
    step_callback: Callable[[str], None] | None = None,
) -> StateGraph:
    """
    Create and compile the SRAG agent graph.

    Args:
        model_name: OpenAI model to use
        temperature: LLM temperature (0 = deterministic)
        use_checkpointer: Whether to use memory checkpointer (disabled by default
            to avoid threading issues with Dash debug mode)
        step_callback: Optional callback for step updates (used for sequential tool execution)

    Returns:
        Compiled StateGraph ready to use

    """
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    agent = create_agent_node(llm)

    # Use sequential tool node if callback provided, otherwise use parallel ToolNode
    if step_callback:
        tools = create_tool_node(ALL_TOOLS, step_callback)
    else:
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

    # Only use checkpointer if explicitly requested (causes issues with Dash debug mode)
    if use_checkpointer:
        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer=checkpointer)
    else:
        app = workflow.compile()

    return app


def _invoke_with_streaming(
    graph: StateGraph,
    message: str,
    thread_id: str,
    config: dict,
    step_callback: Callable[[str], None],
    conversation_history: list[BaseMessage] | None = None,
) -> dict:
    """
    Invoke agent with synchronous streaming support using stream().

    Args:
        graph: Compiled agent graph
        message: User message
        thread_id: Thread ID
        config: Graph configuration
        step_callback: Callback for step updates
        conversation_history: Optional list of previous messages for context

    Returns:
        Agent response dictionary

    """
    initial_state = {
        "messages": _build_messages_list(conversation_history, message),
        "thread_id": thread_id,
    }

    step_callback("Analisando sua solicitação...")
    final_state = None

    try:
        for state in graph.stream(initial_state, config=config, stream_mode="values"):
            messages = state.get("messages", [])
            if messages:
                last_msg = messages[-1]
                if (
                    isinstance(last_msg, AIMessage)
                    and hasattr(last_msg, "tool_calls")
                    and last_msg.tool_calls
                ):
                    step_callback("Preparando análise...")
                elif isinstance(last_msg, AIMessage):
                    step_callback("Gerando resposta...")

            final_state = state

        step_callback("Finalizando resposta...")

        if final_state:
            return final_state

        return graph.invoke(initial_state, config=config)

    except Exception as e:
        logger.warning(f"Stream failed, using invoke: {e}")
        return graph.invoke(initial_state, config=config)


def invoke_agent(
    message: str,
    thread_id: str | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
    temperature: float = DEFAULT_TEMPERATURE,
    step_callback: Callable[[str], None] | None = None,
    conversation_history: list[BaseMessage] | None = None,
) -> dict:
    """
    Invoke the agent with a user message, optionally streaming execution steps.

    Args:
        message: User's message/question
        thread_id: Conversation thread ID (auto-generated if None)
        model_name: OpenAI model to use
        temperature: LLM temperature
        step_callback: Optional callback function called with current step message
        conversation_history: Optional list of previous messages for context

    Returns:
        Dictionary with messages and thread_id

    """
    # Create graph with step_callback to enable sequential tool execution
    graph = create_agent_graph(
        model_name=model_name, temperature=temperature, step_callback=step_callback
    )

    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    if step_callback:
        return _invoke_with_streaming(
            graph, message, thread_id, config, step_callback, conversation_history
        )

    # Standard invoke without streaming
    return graph.invoke(
        {
            "messages": _build_messages_list(conversation_history, message),
            "thread_id": thread_id,
        },
        config=config,
    )
