import json

from gettextbypdf import get_text_and_split

def guardar_fragmentos_en_json(fragmentos_con_metadata, json_path):
    """
    Guarda los fragmentos y su metadata en un archivo JSON.
    """
    with open(json_path, 'w') as json_file:
        json.dump(fragmentos_con_metadata, json_file, indent=4)
    print(f"Fragmentos guardados en {json_path}")

# Ejemplo de uso:
pdf_path = "./downloads/agrometal_2024_Q1_Balance.pdf"
json_path = "./fragmentos_agrometal_2024_Q1.json"

# Generar fragmentos con metadata
fragmentos_con_metadata = get_text_and_split(pdf_path, fragment_size=1000)

# Guardar en JSON
guardar_fragmentos_en_json(fragmentos_con_metadata, json_path)