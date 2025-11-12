# Proyecto_metadatos

**Asistente RAG (Retrieval-Augmented Generation) para consulta de documentos**

Este proyecto implementa un asistente de inteligencia artificial que permite consultar documentos locales (emails, contratos, propuestas, etc.) mediante un pipeline RAG.

---

## Características principales

- Procesamiento de documentos locales y generación de embeddings.
- Vector store persistente con Chroma para consultas rápidas.
- Agente RAG que responde únicamente con información disponible en los documentos.
- Conversación modular y separada del pipeline de ingesta.

---

## Estructura del proyecto

```

Proyecto_metadatos/
├─ src/
│  ├─ agents/            # Definición del agente RAG y tools
│  ├─ conversation/      # Lógica de interacción con el usuario
│  ├─ ingestion/         # Scripts de carga, chunking, embeddings y vector store
│  ├─ metadata/          # Generación y gestión de metadatos
│  ├─ prompts/           # Prompts y plantillas para el agente
│  ├─ chatbot.py         # Streamlit app
│  └─ main.py            # Endpoints de FastAPI
├─ .env                  
├─ .gitignore           
├─ README.md            
└─ requirements.txt     
     

```

## Instalación

1. Clonar el repositorio:

```bash
git clone git@github.com:Bvallegc/proyecto_metadatos.git
cd proyecto_metadatos

```

2. Crear entorno virtual:

```bash

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

```

3. Instalar dependencias:

```bash
pip install -r requirements.txt

```

4. Crear un archivo .env con variables de entorno:

```bash

GROQ_API_KEY=tu_api_key

```

## Uso del Proyecto

1. Ingesta de documentos:

```bash
python src/ingestion/run_ingestion_pipeline.py

```

2. Iniciar el servidor de FastAPI

```bash
python uvicorn main:app --reload

```

3. Levantar la app de streamlit en local

```bash
python streamlit run chatbot.py

```

