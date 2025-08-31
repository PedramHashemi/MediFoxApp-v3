""""""

from typing import Literal

from pydantic import BaseModel, Field
from langgraph.types import Interrupt
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph import MessagesState
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

from models import model_biomistral
from prompts import rag_prompt

def diabetes_specialist(state):
    """Specialized Diabetes Doctor with Rag."""

    print("-> Calling Rag diabetes Artzt")
    question = state['messages'][0]
    prompt = ChatPromptTemplate.from_template(
        template=rag_prompt
    )

    retrieval_chain = (
        {
            "context": retrieve_chroma(),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    result = retrieval_chain.invoke(question[1])
    return {"messages": [result]}