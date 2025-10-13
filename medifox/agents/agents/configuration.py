import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI

class State(TypedDict):
    
    state: Annotated[list, add_messages]



chroma_client = chromadb.HttpClient(
    host="127.0.0.1",
    port=8001,
    settings = Settings(allow_reset=True, anonymized_telemetry=False)
)

chroma_retriever = Chroma(
    client=chroma_client,
    collection_name="pharmacy"
)

reception_llm = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    api_key = "sk-no-key-required"
)

general_llm = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    api_key = "sk-no-key-required"
)

dermatology_llm = ChatOpenAI(
    base_url="http://localhost:8080/v1",
    api_key = "sk-no-key-required"
)