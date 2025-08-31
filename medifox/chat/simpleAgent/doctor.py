""" Simple Agent.

This Agent is a simple doctor just to show us some results in the backend.
"""

from typing import Annotated, Dict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama

from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


model_biomistral = ChatOllama(
    model="hf.co/QuantFactory/BioMistral-7B-GGUF:Q2_K",
    temperature=.3)

def chatbot(state: State):
    return {"messages": [model_biomistral.invoke(state["messages"])]}

def build_agent(checkpointer=None):
    graph_builder = StateGraph(State)
    graph_builder.add_node("doctor", chatbot)
    graph_builder.add_edge(START, "doctor")
    graph_builder.add_edge("doctor", END)
    if checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
    else:
        graph = graph_builder.compile()
    
    return graph

graph = build_agent()

def stream_graph_updates(graph, user_input: str, config: Dict):
    # for index, events in graph.stream(
    #     {"messages": [{"role": "user", "content": user_input}]},
    #     config=config,
    #     stream_mode="values"
    # ):
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values"
    )
    for index, event in enumerate(events):
        if index == 1:
            print(event["messages"][-1].content)
            return event["messages"][-1].content



def ask_fox(question):
    """This function sends the question to the Medifox and returns the answer."""
    return model_biomistral.invoke(question).content
