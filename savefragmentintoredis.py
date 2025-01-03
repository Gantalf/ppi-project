import redis
import json

# Configuración de la conexión a Redis
redis_host = 'localhost'  # O el host donde tengas corriendo Redis
redis_port = 6379         # Puerto por defecto
redis_db = 0             # Base de datos por defecto en Redis

# Crear una conexión con Redis
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

# Función para almacenar un fragmento en Redis
def store_fragment(fragmento):
    """
    Almacena un fragmento de texto en Redis.
    
    Args:
        fragmento (dict): El fragmento que contiene `fragmento_id` y `text`.
    """
    fragmento_id = fragmento["metadata"]["fragmento_id"]
    text = fragmento["text"]

    # Almacenar el fragmento en Redis usando el fragmento_id como la clave
    r.set(fragmento_id, text)
    print(f"Fragmento {fragmento_id} almacenado en Redis.")

# Leer el archivo JSON que contiene los fragmentos
with open("fragmentos_agrometal_2024_q1.json", "r") as f:
    fragmentos_local = json.load(f)

# Recorrer la lista de fragmentos y almacenarlos en Redis
for fragmento in fragmentos_local:
    store_fragment(fragmento)

print("Todos los fragmentos han sido almacenados en Redis.")