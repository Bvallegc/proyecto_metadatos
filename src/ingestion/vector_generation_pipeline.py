from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from pydantic import BaseModel
import json
from rich.console import Console
import os
import dotenv

dotenv.load_dotenv()

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

def split_docs(docs, chunk_size=1000, chunk_overlap=100):
    # Split documents into chunks using RecursiveCharacterTextSplitter to preserve hierarchy.
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    console.log(f"Split into {len(chunks)} chunks.")
    return chunks

def store_in_chroma(chunks, persist_dir="chroma_db"):
    # Generate embeddings for each chunk and store in ChromaDB.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(chunks, embedding=embeddings, persist_directory=persist_dir)
    console.log("Embeddings stored in ChromaDB.")
    return vectordb

class DocumentMetadata(BaseModel):
    title: str
    summary: str
    topics: list[str]
    entities: list[str]

def generate_metadata(text, llm):

    SYSTEM_PROMPT = PromptTemplate.from_template(
    """
    You are a metadata generator. Given the following text, extract the metadata as JSON:
    - Title: a concise title
    - Summary: 2–3 sentence description
    - Topics: list of key themes
    - Entities: list of named entities (people, organizations, locations)

    Text:
    {text}

    Retur valid JSON only.
    """
    )

    chain = SYSTEM_PROMPT | llm
    result = chain.invoke({"text": text})
    
    if hasattr(result, "content"):
        result = result.content

    console.log(f"[blue]LLM Output:[/blue] {result}")

    try:
        return result
    except Exception as e:
        console.log(f"[red]Failed to parse metadata:[/red] {e}")
        return None

def run_pipeline():
    docs = load_docs()
    chunks = split_docs(docs)
    vectordb = store_in_chroma(chunks)
    
    # Generate metadata for each document using llama-3.1-8b-instant
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)

    llm = llm.with_structured_output(DocumentMetadata)

    metadata_list = []
    for doc in docs:
        meta = generate_metadata(doc.page_content[:1000], llm)
        if meta:
            metadata_list.append(meta.model_dump())

    with open("metadata.json", "w") as f:
        json.dump(metadata_list, f, indent=2)
    console.log("[green]Metadata generated and saved to metadata.json[/green]")

if __name__ == "__main__":
    run_pipeline()
