import json
import openai
from pinecone import Pinecone, ServerlessSpec
import fitz  # PyMuPDF
import re
import os
import time 

# Configuración de API de OpenAI y Pinecone
openai_api_key = os.getenv("API_KEY_OPENAI")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai.api_key = openai_api_key
pc = Pinecone(api_key=pinecone_api_key)

# Verificar si el índice ya existe
index_name = "document-embeddings"
# existing_indexes = pc.list_indexes()

# # Comprobar si el índice existe en la lista detallada de índices
# index_exists = any(index.name == index_name for index in existing_indexes.indexes)

# if not index_exists:
#     # Crear el índice si no existe
#     pc.create_index(
#         index_name,
#         dimension=1536,
#         metric="cosine",
#         spec=ServerlessSpec(
#             cloud="aws",
#             region="us-east-1"
#         )
#     )
# else:
#     print(f"El índice '{index_name}' ya existe.")

index = pc.Index(index_name)

# # Función para generar embeddings usando OpenAI
def generar_embedding(texto):
    """
    Genera un embedding para el texto dado utilizando el modelo de OpenAI y maneja errores comunes.
    
    Args:
        texto (str): El texto a procesar para obtener el embedding.
        
    Returns:
        list or None: El embedding del texto como lista de floats, o None si ocurre un error.
    """
    
    if not texto or texto.isspace():
        print("Texto vacío o inválido, omitiendo embedding.")
        return None
    
    # Limitar el texto a los primeros 8191 tokens si es necesario
    texto = texto[:8191]  # Ajuste preventivo para asegurar el límite de tokens
    texto = texto.replace("\n", " ")
    try:
        response = openai.embeddings.create(input=texto, model="text-embedding-ada-002")
        return response.data[0].embedding
    except openai.error.RateLimitError:
        print("Rate limit alcanzado, intenta reducir la frecuencia de las solicitudes.")
    except openai.error.InvalidRequestError as e:
        print(f"Error de solicitud: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    
    return None

# fragmentos_local = {}

# def almacenar_fragmentos_en_pinecone(fragmentos_con_metadata):
#     """
#     Almacena cada fragmento y su metadata en Pinecone.
#     """
#     for fragmento in fragmentos_con_metadata:
#         # Generar el embedding para el texto del fragmento
#         embedding = generar_embedding(fragmento["text"])
        
#         # Verificar que el embedding no sea None antes de intentar almacenarlo
#         if embedding is not None:
#             fragment_id = fragmento["metadata"]["fragmento_id"]
#             metadata = fragmento["metadata"]
            
#             # Guardar el texto completo en el diccionario local
#             fragmentos_local[fragment_id] = fragmento["text"]

#             # Insertar en Pinecone
#             index.upsert([(fragment_id, embedding, metadata)])
#             time.sleep(0.5)
#             print(f"Fragmento {fragment_id} almacenado con éxito en Pinecone.")
#         else:
#             print(f"Error al generar embedding para el fragmento {fragmento['metadata']['fragmento_id']}. Saltando este fragmento.")

# pdf_path = "./downloads/agrometal_2024_Q1_Balance.pdf"

# def get_text_and_split(pdf_path, fragment_size=1000):
#     """
#     Get tex from PDF file, split them in parts and generate metadata for each one.

#     Args:
#         pdf_path (str): path to PDF file.
#         fragment_size (int): number of words per fragment.

#     Returns:
#         list: List of diccionary where each one has you own fragment of text and metadata
#     """
    
#     # Open pdf file
#     doc = fitz.open(pdf_path)
    
#     # get text from all pages
#     tex_complete = ""
#     for page_num in range(doc.page_count):
#         page = doc[page_num]
#         tex_complete += page.get_text("text") + "\n"
    
#     # close PDF file
#     doc.close()
    
#     # split text
#     words = tex_complete.split()
#     fragments = [
#         " ".join(words[i:i+fragment_size])
#         for i in range(0, len(words), fragment_size)
#     ]
    
#     # Generate metadata
#     metadata = generar_metadata_dinamica(pdf_path)

    
#     # Create a list of fragments with you own metadata
#     fragment_with_metadata = []
#     for i, fragment in enumerate(fragments):
#         fragment_metadata = metadata.copy()  # Copiar metadata base
#         fragment_metadata["fragmento_id"] = f"{metadata['company']}_{metadata['year']}_{metadata['quarter']}_part{i+1}"
#         fragment_with_metadata.append({
#             "text": fragment,
#             "metadata": fragment_metadata
#         })
    
#     return fragment_with_metadata


# def generar_metadata_dinamica(pdf_path):
#     """
#     Genera metadata a partir del nombre del archivo PDF, basado en convenciones esperadas.
#     Esta función asume que el nombre del archivo contiene información estructurada sobre la empresa, año y trimestre.
#     Generate metada from file name, based en expected conventions.
#     This function expected that the name of the file be as {companyName}_{year}_{Quarter}_Balance.pdf.

#     Args:
#         pdf_path (str): path PDF file.

#     Returns:
#         dict: diccionary with metadata.
#     """
    
    
#     file_name = pdf_path.split("/")[-1].replace(".pdf", "")
    
#     company = "Unknowell"
#     year = "Unknowell"
#     quarter = "Unknowell"

#     match = re.search(r"(\d{4})_(Q[1-4]|Annual)", file_name)
#     if match:
#         year = match.group(1)
#         quarter = match.group(2)
    
   
#     company_match = re.search(r"^([^_]+)", file_name)
#     if company_match:
#         company = company_match.group(1)

#     # Devolver la metadata en formato diccionario
#     return {
#         "company": company,
#         "year": year,
#         "quarter": quarter
#     }

# # Generar fragmentos con su metadata
# fragmentos_con_metadata = get_text_and_split(pdf_path, fragment_size=2000)

# # Almacenar en Pinecone
# almacenar_fragmentos_en_pinecone(fragmentos_con_metadata)


# -------------- USO --------------------

def buscar_fragmentos_relevantes(pregunta, top_k=5):
    """
    Genera el embedding de la pregunta y busca los fragmentos más relevantes en Pinecone.
    """
    embedding_pregunta = generar_embedding(pregunta)
    resultado = index.query(vector=embedding_pregunta, top_k=top_k, include_metadata=True)
    # Obtener los textos completos desde el diccionario local
    fragmentos_relevantes = [fragmentos_dict[match['id']]['text'] for match in resultado['matches']]
    return fragmentos_relevantes


def consulta_openai(pregunta, fragmentos_relevantes):
    """
    Envía la pregunta y el contexto relevante a OpenAI para obtener una respuesta.
    """
    contexto = "\n".join(fragmentos_relevantes)
    
    # Utiliza ChatCompletion en lugar de Completion
    respuesta = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente de análisis de balances financieros."},
            {"role": "user", "content": f"Contexto: {contexto}\nPregunta: {pregunta}"}
        ]
    )
    
    return respuesta.choices[0].message

# Cargar el JSON de fragmentos en un diccionario local
with open("fragmentos_agrometal_2024_q1.json", "r") as f:
    fragmentos_local = json.load(f)

fragmentos_dict = {fragmento["metadata"]["fragmento_id"]: fragmento for fragmento in fragmentos_local}

pregunta_usuario = "¿Cuál fue el High Spenders de Agrometal en el primer trimestre de 2024?"
fragmentos_relevantes = buscar_fragmentos_relevantes(pregunta_usuario)
respuesta = consulta_openai(pregunta_usuario, fragmentos_relevantes)
print("Pregunta:", pregunta_usuario)
print("Respuesta:", respuesta)