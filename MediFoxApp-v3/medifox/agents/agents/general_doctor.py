"""General Doctor Agent.

TODO: explain the agent.
"""

from typing import Literal

from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command

from models import model_biomistral
from prompts import general_doctor_prompt
from tools.common_tools import make_handoff_tool

general_doctor_tools = [
    make_handoff_tool(agent_name="diabetes_doctor"),
    make_handoff_tool(agent_name="pharmacist")
]

general_doctor = create_react_agent(
    model=model_biomistral,
    tools=general_doctor_tools,
    prompt=(general_doctor_prompt)
)

def call_general_doctor(
        state: MessagesState
) -> Command[Literal["pharmacist", "human"]]: 
    response = general_doctor.invoke(state)
    return Command(update=response, goto="human")