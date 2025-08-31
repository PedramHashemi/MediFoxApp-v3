""" The common tools for all agents.

- *make_handoff_tool*: Create a tool that can return handoff via a Command
- *retrieve_chroma*: Retrieves data from chromadb
"""

import os
from typing import Annotated, Literal

from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, Interrupt
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langgraph.graph import MessagesState, StateGraph, START
from langchain_chroma import Chroma
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

def make_handoff_tool(*, agent_name: str):
    """Create a tool that can return handoff via a Command

    Args:
        agent_name (str): Name of the agent to handoff to.
    """
    
    tool_name = f"transfer_to_{agent_name}"

    @tool(tool_name)
    def handoff_to_agent(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """Ask another agent for help."""
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": tool_name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            # navigate to another agent node in the PAREMT graph
            goto=agent_name,
            graph=Command.PARENT,
            update={"messages": state["messages"] + [tool_message]}
        )

    return handoff_to_agent

def human_node(
        state: MessagesState,
        config
) -> Command[Literal["judge", "human"]]:
    """A node for collecting user input."""

    user_input = Interrupt("waiting response: ")

    langgraph_triggers = config["metadata"]["langgraph_triggers"]
    if len(langgraph_triggers) != 1:
        raise AssertionError("Expected exactly 1 trigger in human node")
    
    active_agent = langgraph_triggers[0].split(":")[1]

    return Command(
        update={
            "messages": [
                {
                    "role": "human",
                    "content": user_input
                }
            ]
        },
        goto=active_agent
    )

def retrieve_chroma():
    """Get the database for vectors. """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cuda"}
    )
    db = Chroma(
        collection_name="MediSource", 
        embedding_function=embeddings,
        persist_directory=os.environ["DB_CHROMA_PATH")
    )
    retriever = db.as_retriever(search_kwargs={"k": 10})
    return retriever