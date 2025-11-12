# src/main.py
from .loaders import load_docs
from .splitters import split_docs
from .embeddings import get_embeddings_model
from .vector_store import store_in_chroma
from src.metadata.generate_metadata import generate_metadata
from langchain_groq import ChatGroq
import json
from rich.console import Console


console = Console()

def run_ingestion_pipeline():
    docs = load_docs()
    # Generar metadatos por DOCUMENTO (antes de chunking)
    llm_metadata = ChatGroq(model="llama-3.1-8b-instant")
    metadata_list = []
    for doc in docs:
        metadata = generate_metadata(doc.page_content, llm_metadata)
        doc.metadata["generated_metadata"] = metadata
        metadata_list.append(metadata)

    with open("metadata.json", "w") as f:
        json.dump(metadata_list, f, indent=2)
    console.log("[green]Metadata generated and saved to metadata.json[/green]")

    chunks = split_docs(docs)
    embeddings = get_embeddings_model()
    metadata = [generate_metadata(chunk.page_content, ChatGroq(model="llama-3.1-8b-instant")) for chunk in chunks]
    vectordb = store_in_chroma(chunks, embeddings)

    return vectordb, metadata