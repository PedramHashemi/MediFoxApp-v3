"""Judge Agent.

TODO: Explain what the judge agent does.
"""

from typing import Literal

from pydantic import BaseModel, Field
from langgraph.types import Interrupt
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph import MessagesState
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

from models import model_biomistral
from prompts import router_prompt

# def human(state: MessagesState) -> Command[Literal["judge_doctor", "human_judge_input"]]

class SpecialistSelectionParser(BaseModel):
    Topic: str = Field(description='Selected Topic', enum=["Diabetes", "Pharmacy", "Not Related"])


@tool
def human_judge_input():
    human_message = Interrupt("human_input")
    return {
        "messages": [
            {
                "role": "human",
                "content": human_message
            }
        ]
    }


@tool
def judge_doctor(state):
    """This one collects information and passes with medical knowledge.
    This one only works as a router"""

    print("-> Calling Judge")
    question = state['messages'][-1]

    prompt = ChatPromptTemplate.from_template(
        router_prompt
    )
    new_llm = model_biomistral.with_structured_output(SpecialistSelectionParser)
    chain = prompt | new_llm
    response = chain.invoke({
        "question": question
    })
    return {"messages": [response.Topic]}