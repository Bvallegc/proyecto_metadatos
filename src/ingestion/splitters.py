from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console

console = Console()

def split_docs(docs, chunk_size=1000, chunk_overlap=100):
    # Split documents into chunks using RecursiveCharacterTextSplitter to preserve hierarchy.
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    console.log(f"Split into {len(chunks)} chunks.")
    return chunks