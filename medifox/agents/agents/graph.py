from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import OpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, START, END
import random

general_llm = OpenAI(
    base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
    api_key = "sk-no-key-required"
)
pharmacy_llm = OpenAI(
    base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
    api_key = "sk-no-key-required"
)
dermatology_llm = OpenAI(
    base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
    api_key = "sk-no-key-required"
)

class State(TypedDict):
    state: Annotated[list, add_messages]

@tool
def call_human(query: str) -> str:
    """If you have any doubts, call the patient.
    If you need more information, call the patient.
    If you want to confirm something, call the patient.
    If you want to narrow down the problem, call the patient to ask
    complementary questions.

    Args:
        query (str): question

    Returns:
        str: human answer
    """
    human_message = interrupt({"query": query})
    return human_message["data"]

@tool
def call_skin_lesion_recognizer() -> str:
    """Call skin lesion recognizer tool if they ask you about
    sking lession.

    Returns:
        str: skin lesion recognizer result
    """
    return random.choice(["Benign", "Malignant", "Uncertain"])

def call_general_doctor(state: State) -> Command[str]:
    pass

def call_pharmacist(state: State) -> Command[str]:
    pass

def call_dermatologist(state: State) -> Command[str]:
    pass

general_doctor_tools = [call_human]
pharmacist_tools = [call_human]
dermatologist_tools = [call_human, call_skin_lesion_recognizer]

# general_llm_with_tools = general_llm.bind_tools(general_doctor_tools)
# pharmacy_llm_with_tools = pharmacy_llm.bind_tools(pharmacist_tools)
# dermatology_llm_with_tools = dermatology_llm.bind_tools(dermatologist_tools)

builder = StateGraph(State)
builder.add_node("general_doctor", call_general_doctor)
builder.add_node("pharmacist", call_pharmacist)
builder.add_node("dermatologist", call_dermatologist)

general_doctor_tool_node = ToolNode(tools = general_doctor_tools)
pharmacist_tool_node = ToolNode(tools = pharmacist_tools)
dermatologist_tool_node = ToolNode(tools = dermatologist_tools)

builder.add_node("general_doctor_tools", general_doctor_tool_node)
builder.add_node("pharmacist_tools", pharmacist_tool_node)
builder.add_node("dermatologist_tools", dermatologist_tool_node)

builder.add_edge(START, "general_doctor")
builder.add_edge("general_doctor", "pharmacist")
builder.add_edge("general_doctor", "dermatologist")

builder.add_edge("general_doctor", "general_doctor_tools")
builder.add_edge("general_doctor_tools", "general_doctor")

builder.add_edge("pharmacist", "pharmacist_tools")
builder.add_edge("pharmacist_tools", "pharmacist")

builder.add_edge("dermatologist", "dermatologist_tools")
builder.add_edge("dermatologist_tools", "dermatologist")

builder.add_edge("general_doctor", END)
builder.add_edge("pharmacist", END)
builder.add_edge("dermatologist", END)

memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)
png_graph = graph.get_graph().draw_mermaid_png()
with open("medifox_graph.png", "wb") as f:
    f.write(png_graph)
