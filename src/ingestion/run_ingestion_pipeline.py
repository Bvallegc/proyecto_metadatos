# src/main.py
from ingestion.loaders import load_docs
from ingestion.splitters import split_docs
from ingestion.embeddings import get_embeddings_model
from ingestion.vector_store import store_in_chroma
from metadata.generate_matadata import generate_metadata
from langchain_groq import ChatGroq



def run_ingestion_pipeline():
    docs = load_docs()
    # Generar metadatos por DOCUMENTO (antes de chunking)
    llm_metadata = ChatGroq(model="llama-3.1-8b-instant")
    for doc in docs:
        metadata = generate_metadata(doc.page_content, llm_metadata)
        doc.metadata["generated_metadata"] = metadata

    chunks = split_docs(docs)
    embeddings = get_embeddings_model()
    metadata = [generate_metadata(chunk.page_content, ChatGroq(model="llama-3.1-8b-instant")) for chunk in chunks]
    vectordb = store_in_chroma(chunks, embeddings)

    return vectordb