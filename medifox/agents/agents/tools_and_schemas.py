import asyncio
import chromadb
from chromadb.config import Settings

chroma_client = chromadb.HttpClient(
    host="127.0.0.1",
    port=8001,
    settings = Settings(allow_reset=True, anonymized_telemetry=False)
)
collection = chroma_client.get_collection(
    name="pharmacy",
)
results = collection.query(
    query_texts=["GEBRAUCHSINFORMATIONEN"],
    n_results=2
)

print(results['documents'])