# Obtener todos los fragmentos almacenados en Pinecone
from testchat import index
import json
from testchat import generar_embedding

json_path = "./fragmentos_agrometal_2024_Q1.json"

def obtener_fragmentos_en_pinecone(ids, batch_size=100):
    """
    Obtiene todos los fragmentos de Pinecone en lotes de IDs.
    
    Args:
        ids (list): Lista de IDs a recuperar del índice.
        batch_size (int): Tamaño del lote de IDs para cada solicitud de `fetch`.

    Returns:
        dict: Diccionario con los fragmentos obtenidos desde Pinecone.
    """
    fragmentos_en_pinecone = {}

    # Procesar en lotes los IDs
    # for i in range(0, len(ids), batch_size):
    #     ids_lote = ids[i:i + batch_size]
    #     resultados = index.fetch(ids=ids_lote, namespace="default")

    #     # Combinar los resultados en el diccionario principal
    #     fragmentos_en_pinecone.update(resultados["vectors"])
    resultados = index.fetch(ids=["id-1", "id-12"], namespace="default")
    fragmentos_en_pinecone.update(resultados.get("vectors"))
    return fragmentos_en_pinecone

# Ejemplo de lista de IDs (cargar desde un archivo JSON si ya tienes esta información)
with open("fragmentos_agrometal_2024_q1.json", "r") as file:
    ids = json.load(file)

# Ejecutar la función para obtener todos los fragmentos en Pinecone
fragmentos = obtener_fragmentos_en_pinecone(ids)

def almacenar_faltantes_en_pinecone(json_path):
    # Cargar fragmentos desde el archivo JSON
    with open(json_path, 'r') as json_file:
        fragmentos_con_metadata = json.load(json_file)
    
    # Verificar y almacenar solo los fragmentos que faltan en Pinecone
    for fragmento in fragmentos_con_metadata:
        fragment_id = fragmento["metadata"]["fragmento_id"]
        
        if fragment_id not in fragmentos:
            # Generar el embedding para el fragmento faltante
            embedding = generar_embedding(fragmento["text"])
            
            # Verificar que el embedding no sea None antes de almacenar
            if embedding is not None:
                metadata = fragmento["metadata"]
                
                # Insertar en Pinecone
                index.upsert([(fragment_id, embedding, metadata)])
                print(f"Fragmento {fragment_id} almacenado con éxito en Pinecone.")
            else:
                print(f"Error al generar embedding para el fragmento {fragment_id}. Saltando este fragmento.")
        else:
            print(f"Fragmento {fragment_id} ya existe en Pinecone.")

# Ejecutar el almacenamiento de faltantes
almacenar_faltantes_en_pinecone(json_path)