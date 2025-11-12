import streamlit as st
import requests
import json
import os
from typing import List, Dict, Any

FASTAPI_BASE_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# --- Funciones de Llamada a la API ---

def call_api(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Función genérica para llamar a los endpoints de la API."""
    url = f"{FASTAPI_BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=300) # Timeout alto para ingesta/chat
        else:
            response = requests.get(url, timeout=5)
            
        response.raise_for_status() # Lanza un error para códigos de estado 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Maneja errores específicos de HTTP (e.g., 400 Bad Request, 500 Internal Server Error)
        st.error(f"Error HTTP del servidor en {endpoint}: {e}")
        try:
            # Intenta obtener el detalle del error si el servidor lo proporcionó
            error_detail = response.json().get("detail", "Error desconocido del servidor.")
            st.error(f"Detalle del servidor: {error_detail}")
        except json.JSONDecodeError:
            st.error("Error: El servidor no devolvió una respuesta JSON válida.")
        return {"status": "error", "message": str(e)}
    except requests.exceptions.RequestException as e:
        # Maneja errores de conexión (servidor no está corriendo, timeout, etc.)
        st.error(f"Error de conexión con el servidor FastAPI: {e}")
        st.warning(f"Asegúrate de que el servidor está corriendo en {FASTAPI_BASE_URL}")
        return {"status": "error", "message": str(e)}

def load_agent_and_update_state():
    """Llama al endpoint /load-agent y actualiza el estado de la aplicación."""
    st.session_state.agent_loading = True
    with st.spinner("Cargando agente RAG... (Esto puede tardar unos segundos)"):
        result = call_api("/load-agent", "POST")
    st.session_state.agent_loading = False
    
    if result.get("status") == "success":
        st.session_state.agent_ready = True
        st.success("✅ Agente RAG cargado y listo para chatear.")
    else:
        st.session_state.agent_ready = False
        st.error(f"❌ Falló la carga del agente: {result.get('message', 'Verifica la consola de FastAPI.')}")

def ingest_data_and_update_state():
    """Llama al endpoint /ingest y actualiza el estado de la aplicación."""
    st.session_state.ingesting = True
    with st.spinner("Ejecutando pipeline de ingesta... (Esto puede tardar varios minutos dependiendo de los datos)"):
        result = call_api("/ingest", "POST")
    st.session_state.ingesting = False
    
    if result.get("status") == "success":
        st.session_state.ingestion_message = "✅ Ingesta de datos completada. ¡Ahora debes recargar el Agente RAG!"
        st.session_state.agent_ready = False # Invalida el agente actual
        st.success(st.session_state.ingestion_message)
    else:
        st.session_state.ingestion_message = f"❌ Falló la ingesta: {result.get('message', 'Verifica la consola de FastAPI.')}"
        st.error(st.session_state.ingestion_message)

def get_agent_response(prompt: str) -> str:
    """Llama al endpoint /chat."""
    data = {"query": prompt}
    result = call_api("/chat", "POST", data)
    
    if "response" in result:
        return result["response"]
    else:
        # Si hay un error HTTP o de conexión, call_api ya lo habrá mostrado con st.error
        return "Disculpa, no pude obtener una respuesta. Revisa los mensajes de error arriba."

# --- Inicialización del Estado de Streamlit ---

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'agent_ready' not in st.session_state:
    st.session_state.agent_ready = False

if 'agent_loading' not in st.session_state:
    st.session_state.agent_loading = False

if 'ingesting' not in st.session_state:
    st.session_state.ingesting = False

if 'ingestion_message' not in st.session_state:
    st.session_state.ingestion_message = ""

# --- Interfaz de Usuario de Streamlit ---

st.set_page_config(page_title="Chatbot RAG con Streamlit y FastAPI", layout="wide")

st.title("🧠 Chatbot RAG con FastAPI y Streamlit")
st.caption(f"Conectado a FastAPI en: `{FASTAPI_BASE_URL}`")

# --- Barra Lateral para Control y Estado ---
with st.sidebar:
    st.header("⚙️ Control del Agente RAG")
    
    # --- 1. Botón de Carga del Agente ---
    st.subheader("Paso 1: Cargar Agente")
    st.write("Carga la base de datos vectorial y el modelo LLM en la memoria del servidor FastAPI.")
    
    agent_status_msg = "🟢 LISTO" if st.session_state.agent_ready else "🔴 INACTIVO"
    st.markdown(f"**Estado del Agente:** {agent_status_msg}")
    
    # El botón llama a la función de carga
    st.button(
        "Cargar Agente RAG", 
        on_click=load_agent_and_update_state,
        disabled=st.session_state.agent_loading # Deshabilitar si ya está cargando
    )
    
    st.divider()

    # --- 2. Botón de Ingesta de Datos ---
    st.subheader("Paso 2: Ingesta de Datos")
    st.write("Procesa documentos y genera nuevos embeddings. REQUIERE RECARGAR el agente después.")
    
    # El botón llama a la función de ingesta
    st.button(
        "Ejecutar Ingesta", 
        on_click=ingest_data_and_update_state,
        disabled=st.session_state.ingesting # Deshabilitar si ya está ingiriendo
    )
    
    if st.session_state.ingestion_message:
         st.info(st.session_state.ingestion_message)

# --- Contenido Principal: Interfaz de Chat ---

# Mostrar mensajes de chat anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Lógica de la Entrada de Usuario ---

# El chat input solo se habilita si el agente está listo
if st.session_state.agent_ready:
    prompt = st.chat_input("¡Haz tu pregunta sobre los documentos!")
    
    if prompt:
        # 1. Añadir mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Obtener respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("El agente está pensando..."):
                response = get_agent_response(prompt)
                st.markdown(response)

        # 3. Añadir respuesta del agente al historial
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("⚠️ Por favor, haz clic en 'Cargar Agente RAG' en la barra lateral para empezar a chatear.")