# src/main.py
import dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rich.console import Console
from src.ingestion.run_ingestion_pipeline import run_ingestion_pipeline
from src.service.rag_service import load_rag_agent, get_chat_response

dotenv.load_dotenv()

app = FastAPI()
console = Console()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

class IngestResponse(BaseModel):
    status: str
    message: str

class LoadResponse(BaseModel):
    status: str
    message: str

rag_agent_executor = None

@app.post("/ingest", response_model=IngestResponse)
async def ingest_data():
    """
    Endpoint para ejecutar el pipeline de ingesta.
    La lógica ya estaba separada, así que esto no cambia.
    """
    console.log("🏃‍♂️ Iniciando pipeline de ingesta...")
    try:
        run_ingestion_pipeline()
        console.log("✅ Ingesta completada.")
        return IngestResponse(
            status="success", 
            message="Ingesta de datos completada. Llama a /load-agent para recargar el agente."
        )
    except Exception as e:
        console.log(f"❌ Error durante la ingesta: {e}")
        raise HTTPException(status_code=500, detail=f"Error de ingesta: {e}")

@app.post("/load-agent", response_model=LoadResponse)
async def load_agent_endpoint():
    """
    Endpoint para cargar el agente RAG.
    Ahora solo llama a la función de servicio.
    """
    global rag_agent_executor
    
    console.log("🔄 Recibida solicitud para cargar agente...")
    try:
        rag_agent_executor = load_rag_agent()
        console.log("✅ Agente RAG cargado y listo (vía servicio).")
        return LoadResponse(status="success", message="Agente cargado exitosamente.")
        
    except Exception as e:
        console.log(f"❌ Error al cargar el agente: {e}")
        rag_agent_executor = None
        raise HTTPException(status_code=500, detail=f"Error al cargar el agente: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint para conversar con el agente.
    Ahora solo llama a la función de servicio.
    """
    if rag_agent_executor is None:
        raise HTTPException(status_code=400, detail="Error: El agente RAG no está inicializado. Llama a /load-agent primero.")
        
    console.log(f"Recibida query: {request.query}")
    
    try:
        response_text = get_chat_response(rag_agent_executor, request.query)
        console.log(f"Respuesta generada: {response_text}")
        return ChatResponse(response=response_text)
    except Exception as e:
        console.log(f"❌ Error durante el chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {e}")

@app.get("/")
async def root():
    return {"message": "Servidor RAG con FastAPI está funcionando."}


# --- Ejecución del Servidor (sin cambios) ---
if __name__ == "__main__":
    console.log("Iniciando servidor Uvicorn en http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)