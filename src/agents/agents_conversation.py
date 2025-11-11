# src/main.py
from agents.tools import make_retrieve_context_tool
from agents.agent import create_rag_agent
from langchain_groq import ChatGroq
import dotenv
from prompts.rag_prompt import RAG_AGENT_PROMPT
from rich.console import Console

console = Console()

def agent_conversation(vectordb):
    retrieve_tool = make_retrieve_context_tool(vectordb)
    tools = [retrieve_tool]

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)

    agent = create_rag_agent(llm, tools=tools, prompt=RAG_AGENT_PROMPT)

    while True:
        query = input("💬 Tu pregunta: ").strip()
        
        # Condiciones de salida
        if query.lower() in ["salir", "exit", "quit", ""]:
            console.print("[bold red]👋 ¡Hasta luego![/bold red]")
            break
        
        try:
            # Invocar el agente
            response = agent.invoke({"messages": [("user", query)]})
            
            # Extraer la respuesta final
            final_message = response["messages"][-1].content
            console.print(f"\n[bold cyan]🤖 Respuesta:[/bold cyan] {final_message}\n")
            
        except Exception as e:
            console.print(f"[bold red]❌ Error:[/bold red] {e}\n")