"""Define the agent graph for MediFox application."""

from typing import Literal
import json
import re

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages
from tools_and_schemas import call_human, call_skin_lesion_recognizer
from configuration import (
    chroma_client,
    reception_llm, general_llm,
    dermatology_llm
)

class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    goto: Literal['', 'general_doctor', 'pharmacist', 'dermatologist']
    current_node: Literal['reception', 'general_doctor', 'pharmacist', 'dermatologist']

class ReceptionOutput(BaseModel):
    specialist: Literal['general_doctor', 'pharmacist', 'dermatologist'] = Field(
        description="The specialist to route the patient to."
    )

def reception(state: State):
    """Route the patient to the appropriate specialist based on their query."""

    # reception_llm_structured = reception_llm.with_structured_output(ReceptionOutput)

    prompt = PromptTemplate(
        template = """
        You are only a receptionist. Your job is to route the patient to the right specialist.
        Keep the greetings and daily talks to a minimum and focus on the routing.
        If the question is about dermatology, return dermatologist.
        If the question is about pharmacy, return pharmacist. Otherwise, return general_doctor
        don't ask further questions.
        return the result i the following JSON format: {{ "specialist": "<specialist>" }}.
        Here is the user question: {question}."""
    )

    chain = prompt | reception_llm

    messages = state["messages"]
    question = messages[-1].content
    print(question)

    send_to_specialist = chain.invoke({"question": question})
    def extract_json(text):
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    send_to_specialist = extract_json(send_to_specialist.content)
    return {"messages": send_to_specialist.get("specialist")}

def route_to_specialist(state: State) -> Literal['general_doctor', 'pharmacist', 'dermatologist']:
   print(state)
   return state["messages"][-1].content

def call_general_doctor(state: State):
    return {"messages": "General doctor here ..."}

def call_pharmacist(state: State):
    # question = "what are the side effects of alfosozin?"
    # pharmacy_llm = ChatOpenAI(
    #     base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
    #     api_key = "sk-no-key-required"
    # )
    # pharmacy_llm_with_tools = pharmacy_llm.bind_tools(pharmacist_tools)
    # prompt = PromptTemplate(
    #     template = """
    #     You are a helpful pharmacist assistant. Use the tool to answer the question.
    #     Here is the retrieved information from pharmacy database: {context}
    #     Here is the user question {question}.
    #     If the document does not contain the answer, just say you don't know.""",
    #     input_variables = ["context", "question"],
    # )
    # chain = prompt | pharmacy_llm_with_tools
    # messages = state["messages"]
    # question = messages[-1]["content"]
    # return {"messages": }
    return {"messages": "Pharmacist here ..."}


def call_dermatologist(state: State):
    return {"messages": "Dermatologist here ..."}

# general_doctor_tools = [call_human]
# pharmacist_tools = [call_human]
# dermatologist_tools = [call_human, call_skin_lesion_recognizer]

# general_llm_with_tools = general_llm.bind_tools(general_doctor_tools)
# dermatology_llm_with_tools = dermatology_llm.bind_tools(dermatologist_tools)

builder = StateGraph(State)
builder.add_node("reception", reception)
builder.add_node("general_doctor", call_general_doctor)
builder.add_node("pharmacist", call_pharmacist)
builder.add_node("dermatologist", call_dermatologist)

# general_doctor_tool_node = ToolNode(tools = general_doctor_tools)
# pharmacist_tool_node = ToolNode(tools = pharmacist_tools)
# dermatologist_tool_node = ToolNode(tools = dermatologist_tools)

# builder.add_node("general_doctor_tools", general_doctor_tool_node)
# builder.add_node("pharmacist_tools", pharmacist_tool_node)
# builder.add_node("dermatologist_tools", dermatologist_tool_node)

builder.add_edge(START, "reception")
builder.add_conditional_edges(
    "reception",
    route_to_specialist,
    {
        "general_doctor": "general_doctor",
        "pharmacist": "pharmacist",
        "dermatologist": "dermatologist",
    }
)

# builder.add_edge("general_doctor", "general_doctor_tools")
# builder.add_edge("general_doctor_tools", "general_doctor")

# builder.add_edge("pharmacist", "pharmacist_tools")
# builder.add_edge("pharmacist_tools", "pharmacist")

# builder.add_edge("dermatologist", "dermatologist_tools")
# builder.add_edge("dermatologist_tools", "dermatologist")


builder.add_edge("general_doctor", END)
builder.add_edge("pharmacist", END)
builder.add_edge("dermatologist", END)

memory = InMemorySaver()
chatter = builder.compile(checkpointer=memory)
png_graph = chatter.get_graph().draw_mermaid_png()
with open("medifox_graph.png", "wb") as f:
    f.write(png_graph)


if __name__ == "__main__":
    config = {"configurable": {"user_id": 1, "thread_id": 1}}
    # while True:
    input = {"messages": HumanMessage("I have a skin lesion that looks suspicious. What should I do?")}
    input = {"messages": HumanMessage("I'm using a medication named alfusozin, What are the side effects of alfosozin?")}
    input = {"messages": HumanMessage("I have a headache and fever. What should I do?")}
    print(chatter.invoke(input=input, config=config))
    # for event in chatter.stream(input=input, stream_mode=True, config=config):
    #     print(event[-1]["data"]["chunk"].content)
