from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from tools import get_current_time_tool, search_database
from tool_node import SQLToolNode
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = ChatOpenAI(model="gpt-4o-mini")
tools = [get_current_time_tool, search_database]
llm_with_tools = llm.bind_tools(tools)


def call_model(state: State):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

graph_builder.add_node("agent", call_model)
graph_builder.add_node("tools", SQLToolNode(tools))


graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges(
    "agent",
    route_tools,
    {"tools": "tools", END: END},
)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile(checkpointer=memory)