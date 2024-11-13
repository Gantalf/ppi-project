import fitz  
import re

def get_text_and_split(pdf_path, fragment_size=2000):
    """
    Get tex from PDF file, split them in parts and generate metadata for each one.

    Args:
        pdf_path (str): path to PDF file.
        fragment_size (int): number of words per fragment.

    Returns:
        list: List of diccionary where each one has you own fragment of text and metadata
    """
    
    # Open pdf file
    doc = fitz.open(pdf_path)
    
    # get text from all pages
    tex_complete = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        tex_complete += page.get_text("text") + "\n"
    
    # close PDF file
    doc.close()
    
    # split text
    words = tex_complete.split()
    fragments = [
        " ".join(words[i:i+fragment_size])
        for i in range(0, len(words), fragment_size)
    ]
    
    # Generate metadata
    metadata = generar_metadata_dinamica(pdf_path)

    
    # Create a list of fragments with you own metadata
    fragment_with_metadata = []
    for i, fragment in enumerate(fragments):
        fragment_metadata = metadata.copy()  # Copiar metadata base
        fragment_metadata["fragmento_id"] = f"{metadata['company']}_{metadata['year']}_{metadata['quarter']}_part{i+1}"
        fragment_with_metadata.append({
            "text": fragment,
            "metadata": fragment_metadata
        })
    
    return fragment_with_metadata


def generar_metadata_dinamica(pdf_path):
    """
    Genera metadata a partir del nombre del archivo PDF, basado en convenciones esperadas.
    Esta función asume que el nombre del archivo contiene información estructurada sobre la empresa, año y trimestre.
    Generate metada from file name, based en expected conventions.
    This function expected that the name of the file be as {companyName}_{year}_{Quarter}_Balance.pdf.

    Args:
        pdf_path (str): path PDF file.

    Returns:
        dict: diccionary with metadata.
    """
    
    
    file_name = pdf_path.split("/")[-1].replace(".pdf", "")
    
    company = "Unknowell"
    year = "Unknowell"
    quarter = "Unknowell"

    match = re.search(r"(\d{4})_(Q[1-4]|Annual)", file_name)
    if match:
        year = match.group(1)
        quarter = match.group(2)
    
   
    company_match = re.search(r"^([^_]+)", file_name)
    if company_match:
        company = company_match.group(1)

    # Devolver la metadata en formato diccionario
    return {
        "company": company,
        "year": year,
        "quarter": quarter
    }

# Ejemplo de uso
pdf_path = "./downloads/agrometal_2024_Q1_Balance.pdf"  # Reemplaza con la ruta real de tu archivo PDF
fragmentos_con_metadata = get_text_and_split(pdf_path)











# Mostrar los primeros fragmentos para verificar
for fragmento in fragmentos_con_metadata[:3]:
    print("Fragmento:", fragmento["text"][:100])  # Mostrar los primeros 100 caracteres del fragmento
    print("Metadata:", fragmento["metadata"])
    print("------")
