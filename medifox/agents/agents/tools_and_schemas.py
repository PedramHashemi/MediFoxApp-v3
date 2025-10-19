from langchain_core.tools import tool
from langgraph.types import interrupt
import random

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