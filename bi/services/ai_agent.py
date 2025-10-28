from llama_index.core import VectorStoreIndex, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage import StorageContext
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import chromadb
import pandas as pd
from ..models import MovimientoEconomico

import requests
import json

url="http://localhost:11434/api/generate"

def generar_respuesta(pregunta):
    data = {
        "model": "mistral:7b",
        "prompt": pregunta,
        "stream": True
    }
    with requests.post(url, json=data, stream=True) as response:
        for line in response.iter_lines():
            if line:
                try:
                    token_data = json.loads(line.decode("utf-8"))
                    if "response" in token_data:
                        yield token_data["response"]
                except:
                    continue

def construir_indice():
    client = chromadb.Client()
    chroma_collection = client.get_or_create_collection("movimientos")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    df = pd.DataFrame(list(MovimientoEconomico.objects.all().values(
        'descripcion', 'categoria', 'naturaleza', 'cantidad', 'unidad',
        'precio_unitario', 'total', 'fecha', 'informe__observaciones'
    )))
    df.rename(columns={'informe__observaciones': 'observacion'}, inplace=True)

    documentos = [
        Document(
            text=f"Descripción: {row['descripcion']}. Categoría: {row['categoria']}. "
                 f"Total: {row['total']}. Observación: {row['observacion']}. Fecha: {row['fecha']}"
        )
        for _, row in df.iterrows()
    ]

    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = VectorStoreIndex.from_documents(documentos, storage_context=storage_context, embed_model=embed_model)
    return index

def construir_prompt(pregunta_usuario, info_usuario, contexto):
    prompt = f"""Información del usuario:
    - Nombre: {info_usuario['nombre']}
    - Username: {info_usuario['username']}
    - Correo: {info_usuario['correo']}
    - Rol: {info_usuario['rol']}

    Contexto financiero relevante:
    {contexto}

    Pregunta: {pregunta_usuario}
    Responde de manera clara y concisa:
    """
    return prompt
