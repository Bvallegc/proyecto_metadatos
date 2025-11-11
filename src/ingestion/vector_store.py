from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from rich.console import Console
import os

console = Console()

def store_in_chroma(chunks, embeddings, persist_dir="chroma_db"):
    console.log(f"[yellow]First chunk metadata:[/yellow] {chunks[0].metadata}")
    # Generate embeddings for each chunk and store in ChromaDB.
    vectordb = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=persist_dir)
    console.log("Embeddings stored in ChromaDB.")
    return vectordb


def load_chroma_store(persist_path: str):
    """
    Carga un vector store de Chroma previamente persistido.
    """
    vectordb = Chroma(persist_directory=persist_path)
    return vectordb