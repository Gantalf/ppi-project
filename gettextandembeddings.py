import fitz  # PyMuPDF
import openai
import tiktoken  # Para contar tokens en los fragmentos
import re

# Configura tu clave de API de OpenAI
openai.api_key = "TU_CLAVE_DE_OPENAI"

def extract_text_from_pdf(file_path):
    """
    Extrae y fragmenta el texto de un archivo PDF.
    """
    doc = fitz.open(file_path)
    all_text = []
    
    # Itera sobre cada página para extraer el texto
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text("text")
        
        # Divide el texto de cada página en líneas y elimina los espacios innecesarios
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        # Agrega el contenido de cada página como un bloque de texto
        all_text.extend(cleaned_lines)
    
    doc.close()
    return all_text

def split_text_into_chunks(text, max_tokens=500):
    """
    Divide el texto en fragmentos que no excedan el límite de tokens especificado.
    """
    tokenizer = tiktoken.get_encoding("cl100k_base")  # Tokenizer para conteo de tokens
    chunks = []
    current_chunk = []

    for line in text:
        line_tokens = len(tokenizer.encode(line))
        
        # Si agregar esta línea excede el límite, guarda el fragmento actual
        if sum(len(tokenizer.encode(line)) for line in current_chunk) + line_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
        
        current_chunk.append(line)
    
    # Guarda el último fragmento
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def generate_embeddings(chunks, metadata):
    """
    Genera embeddings para cada fragmento de texto y añade los metadatos correspondientes.
    """
    embeddings_data = []
    
    for chunk in chunks:
        response = openai.Embedding.create(input=chunk, model="text-embedding-ada-002")  # Modelo para generar embeddings
        embedding = response['data'][0]['embedding']
        
        # Agrega cada embedding con su metadata a la lista
        embeddings_data.append({
            "embedding": embedding,
            "metadata": metadata,
            "text": chunk  # Mantiene el texto para facilitar la referencia
        })
    
    return embeddings_data

# Ejemplo de uso con el archivo PDF y generación de embeddings
file_path = 'Estados Financieros_0924_Ind..pdf'  # Archivo PDF
text_data = extract_text_from_pdf(file_path)

# Fragmenta el texto en partes de 500 tokens
chunks = split_text_into_chunks(text_data, max_tokens=500)

# Define la metadata (nombre de la empresa, año y trimestre)
metadata = {
    "empresa": "Nombre de la Empresa",
    "año": "2024",
    "trimestre": "Q3"
}

# Genera los embeddings con la metadata correspondiente
embeddings = generate_embeddings(chunks, metadata)

# Imprime un resumen de los embeddings generados
for idx, data in enumerate(embeddings):
    print(f"Fragmento {idx + 1}:")
    print(f"Texto: {data['text'][:100]}...")  # Muestra los primeros 100 caracteres
    print(f"Metadata: {data['metadata']}")
    print(f"Embedding (longitud): {len(data['embedding'])}")
    print("-" * 40)
