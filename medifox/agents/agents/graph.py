from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.tools import tool
from langgraph.graph.messages import add_messages
from langgraph.prebuilt import ToolNode, conditional_node
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, Start, End
import random

general_llm = 
pharmacy_llm = 
dermatology_llm = 

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
    

general_doctor_tools = ['call_human']
pharmacist_tools = ['call_human']
dermatologist_tools = ['call_human', 'call_skin_lesion_recognizer']

llm_with_tools = general_llm.bind_tools(general_doctor_tools)
llm_with_tools = pharmacy_llm.bind_tools(pharmacist_tools)
llm_with_tools = dermatology_llm.bind_tools(dermatologist_tools)


builder = StateGraph(State)
builder.add_node("general_doctor", "call_general_doctor")
builder.add_node("pharmacist", "call_pharmacist")
builder.add_node("dermatologist", "call_dermatologist")

builder.add_edge(Start, "general_doctor")
builder.add_edge("general_doctor", "pharmacist")
builder.add_edge("general_doctor", "dermatologist")
builder.add_edge("general_doctor", End)
builder.add_edge("pharmacist", End)
builder.add_edge("dermatologist", End)
