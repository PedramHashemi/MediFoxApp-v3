""" All the models (LLMs) that we use.

TODO: complete this documentation. Which models I'm going to include

all the models will be called like so: model_{model_name}
"""

import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

model_biomistral = ChatOllama(
    model="hf.co/QuantFactory/BioMistral-7B-GGUF:Q2_K",
    temperature=.3
)

model_llama32 = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    model="llama3.2",
    api_key="ollama"
)

model_geminiflash = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-8b",
    google_api_key=os.getenv["GEMINI_API_KEY"],
    temperature=0.7
)