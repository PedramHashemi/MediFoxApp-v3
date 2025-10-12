import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma

chroma_client = chromadb.HttpClient(
    host="127.0.0.1",
    port=8001,
    settings = Settings(allow_reset=True, anonymized_telemetry=False)
)

chroma_retriever = Chroma(
    client=chroma_client,
    collection_name="pharmacy"
)