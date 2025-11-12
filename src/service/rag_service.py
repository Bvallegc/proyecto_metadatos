# src/services/rag_service.py
from langchain_groq import ChatGroq
from src.agents.tools import make_retrieve_context_tool
from src.agents.agent import create_rag_agent
from src.prompts.rag_prompt import RAG_AGENT_PROMPT
from src.ingestion.vector_store import load_chroma_store
from rich.console import Console

console = Console()

def load_rag_agent():
    """
    Carga la base de datos vectorial, configura el LLM y las herramientas,
    y devuelve el agente RAG listo para usarse.
    """
    console.log("Cargando Vector DB desde el servicio...")
    vectordb = load_chroma_store(persist_path="chroma_db")
    
    console.log("Creando herramientas de retrieval...")
    retrieve_tool = make_retrieve_context_tool(vectordb)
    tools = [retrieve_tool]

    console.log("Configurando LLM (llama-3.1-8b-instant)...")
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)

    console.log("Creando agente RAG...")
    agent_executor = create_rag_agent(llm, tools=tools, prompt=RAG_AGENT_PROMPT)
    
    return agent_executor

def get_chat_response(agent_executor, query: str) -> str:
    """
    Invoca al agente RAG con una nueva consulta de usuario
    y extrae la respuesta final.
    """
    console.log("Invocando agente con la consulta...")
    try:
        response = agent_executor.invoke({"messages": [("user", query)]})
        
        final_message = response["messages"][-1].content
        return final_message
        
    except Exception as e:
        console.log(f"❌ Error al invocar el agente: {e}")
        raise