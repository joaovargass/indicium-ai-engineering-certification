"""
LangGraph StateGraph implementation for SRAG agent.

Creates an execution graph that receives user messages, decides tool usage,
executes tools, and generates responses while maintaining conversation history.
"""

import time
import uuid
from typing import Annotated, Callable, Literal, TypedDict

from dotenv import load_dotenv
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
from tools import ALL_TOOLS

load_dotenv()

# Tool name to step message mapping
_TOOL_STEP_MAPPING = {
    "get_case_increase_rate": "Calculando taxa de aumento de casos...",
    "get_mortality_rate": "Calculando taxa de mortalidade...",
    "get_icu_occupancy_rate": "Calculando taxa de ocupação de UTI...",
    "get_vaccination_rate": "Calculando taxas de vacinação...",
    "get_daily_chart_json": "Gerando gráfico de casos diários...",
    "get_monthly_chart_json": "Gerando gráfico de casos mensais...",
    "generate_download_report": "Gerando relatório completo...",
    "generate_chat_report": "Gerando relatório interativo...",
    "search_srag_news_tool": "Buscando notícias de saúde...",
}


class AgentState(TypedDict):
    """State schema for the agent graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str


def _convert_ui_messages_to_langchain(ui_messages: list[dict]) -> list[BaseMessage]:
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


def create_sequential_tool_node(
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
    # Create a tool lookup dictionary
    tool_dict = {tool.name: tool for tool in tools}

    def sequential_tool_node(state: AgentState) -> AgentState:
        """Execute tools sequentially, updating callback for each."""
        messages = state["messages"]
        tool_messages = []

        # Get the last message which should contain tool calls
        last_message = messages[-1]
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"messages": []}

        # Execute each tool call sequentially
        for tool_call in last_message.tool_calls:
            # Handle both dict and ToolCall object formats
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "")
                tool_id = tool_call.get("id", "")
                tool_args = tool_call.get("args", {})
            else:
                # ToolCall object (Pydantic model) - access attributes directly
                tool_name = getattr(tool_call, "name", "")
                tool_id = getattr(tool_call, "id", "")
                tool_args = getattr(tool_call, "args", {})

            # Update step callback before executing tool
            if step_callback:
                step_message = _TOOL_STEP_MAPPING.get(
                    tool_name, f"Executando {tool_name}..."
                )
                step_callback(step_message)
                # Keep message visible for at least 1 second
                time.sleep(1.0)

            # Get the tool and execute it
            if tool_name in tool_dict:
                tool = tool_dict[tool_name]
                try:
                    # Execute the tool
                    result = tool.invoke(tool_args)

                    # Convert result to string if needed
                    if isinstance(result, dict):
                        import json
                        content = json.dumps(result, ensure_ascii=False)
                    else:
                        content = str(result)

                    # Create tool message
                    tool_message = ToolMessage(
                        content=content,
                        tool_call_id=tool_id,
                    )
                    tool_messages.append(tool_message)
                except Exception as e:
                    # Create error message
                    error_content = f"Error: {str(e)}"
                    tool_message = ToolMessage(
                        content=error_content,
                        tool_call_id=tool_id,
                    )
                    tool_messages.append(tool_message)

        # After all tools complete, show processing message
        if step_callback and tool_messages:
            step_callback("Processando resultados...")
            time.sleep(0.5)  # Brief pause to show the message

        return {"messages": tool_messages}

    return sequential_tool_node


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Route to tools node if agent has tool calls (agent interpreted confirmation).

    The agent uses LLM interpretation to determine if user confirmed.
    If agent calls tools, it means it interpreted the user's message as confirmation.

    Args:
        state: Current graph state

    Returns:
        "tools" if agent wants to call tools, "end" otherwise

    """
    messages = state["messages"]
    if not messages:
        return "end"

    last_message = messages[-1]

    # If agent has tool calls, it means it interpreted user confirmation
    # Trust the agent's LLM-based interpretation
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"


def create_agent_graph(
    model_name: str = "gpt-5-nano",
    temperature: float = 0.0,
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
        tools = create_sequential_tool_node(ALL_TOOLS, step_callback)
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
        # Use stream_mode="values" to get full accumulated state after each node
        for state in graph.stream(initial_state, config=config, stream_mode="values"):
            # state is the full accumulated state after each node execution
            messages = state.get("messages", [])
            if messages:
                last_msg = messages[-1]
                # Check if last message is an AI message with tool calls (agent deciding to use tools)
                if isinstance(last_msg, AIMessage) and hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    # Agent decided to use tools - show preparation message before tools execute
                    step_callback("Preparando análise...")
                # Check if last message is a ToolMessage (tools finished executing)
                # Note: sequential_tool_node already shows "Compilando métricas..." after all tools
                # So we don't override here - the tool node messages take precedence
                elif isinstance(last_msg, ToolMessage):
                    # Tools are executing - sequential_tool_node handles the messages
                    # Don't override with generic message
                    pass
                # Final AI message (no tool calls = final response)
                elif isinstance(last_msg, AIMessage) and not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
                    # Agent is generating final response after processing tool results
                    step_callback("Gerando resposta...")

            final_state = state

        step_callback("Finalizando resposta...")

        if final_state:
            return final_state

        return graph.invoke(initial_state, config=config)

    except Exception as e:
        print(f"Warning: stream failed, using invoke: {e}")
        return graph.invoke(initial_state, config=config)


def invoke_agent(
    message: str,
    thread_id: str | None = None,
    model_name: str = "gpt-5-nano",
    temperature: float = 0.0,
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
