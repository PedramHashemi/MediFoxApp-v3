""""""

import random
from langchain_core.tools import tool
from langgraph.types import interrupt
from langchain.tools.retriever import create_retriever_tool

from configuration import chroma_retriever

@tool
def pharmacy_retriever_tool(query: str) -> str:
    """Retrieve information from the pharmacy knowledge base."""
    retrieved_docs = chroma_retriever.similarity_search(query, k=3)
    serialized_docs = "\n".join(
        (f"Source: {doc.metadata}, Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized_docs, retrieved_docs

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