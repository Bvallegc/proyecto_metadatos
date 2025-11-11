# src/main.py
from agents.tools import make_retrieve_context_tool
from agents.agent import create_rag_agent
from langchain_groq import ChatGroq
import dotenv
from prompts.rag_prompt import RAG_AGENT_PROMPT
from rich.console import Console
from ingestion.run_ingestion_pipeline import run_ingestion_pipeline
from ingestion.vector_store import load_chroma_store
from agents.agents_conversation import agent_conversation

console = Console()
dotenv.load_dotenv()

def main():
    # vectordb = run_ingestion_pipeline()
    vectordb = load_chroma_store(persist_path="chroma_db")
    agent_conversation(vectordb)

if __name__ == "__main__":
    main()
