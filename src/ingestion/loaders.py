from langchain_community.document_loaders import TextLoader, PyPDFLoader
import os
from rich.console import Console

console = Console()

def load_docs(data_path="data"):
    docs = []
    for file in os.listdir(data_path):
        path = os.path.join(data_path, file)
        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
        else:
            loader = TextLoader(path)
        docs.extend(loader.load())
    console.log(f"Loaded {len(docs)} documents.")
    return docs