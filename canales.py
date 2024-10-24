import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from ppi_client.ppi import PPI
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import pytz
import numpy as np
from dateutil import parser
from scipy.signal import argrelextrema
from sklearn.linear_model import LinearRegression

load_dotenv()

api_key = os.getenv('API_KEY')

ppi = PPI(sandbox=False)

ppi.account.login_api('c2ZHRVdOb1hLZHBHOUpMeDBpZFc=', api_key)

def get_historical_volume_data():
    """Función para obtener los datos históricos de volumen y precio."""
    return ppi.marketdata.search(
        "GD35", "Bonos", "A-24HS",
        datetime(2024, 1, 1),
        datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
    )

# Obtener los datos
info = get_historical_volume_data()

# Preparar listas para fechas y precios
dates = []
prices = []

for data in info:
    date = parser.parse(data['date'])
    price = data['price']
    dates.append(date)
    prices.append(price)

# Convertir precios y fechas a arrays NumPy para la regresión
prices_np = np.array(prices)
dates_ordinal = np.array([d.toordinal() for d in dates]).reshape(-1, 1)

# Ajuste de regresión lineal para la línea media
reg_media = LinearRegression().fit(dates_ordinal, prices_np)
linea_media = reg_media.predict(dates_ordinal)

# Calcular desviaciones independientes para la resistencia y el soporte
desviacion_superior = np.max(prices_np - linea_media)  # Máxima desviación hacia arriba
desviacion_inferior = np.max(linea_media - prices_np)  # Máxima desviación hacia abajo

# Crear las líneas del canal
linea_superior = linea_media + desviacion_superior
linea_inferior = linea_media - desviacion_inferior # Ajustamos un poco más abajo el soporte
linea_media_ajustada = (linea_superior + linea_inferior) / 2
# Crear la figura del gráfico
plt.figure(figsize=(12, 6))

# Graficar la evolución del precio original
plt.plot(dates, prices, marker='o', linestyle='-', linewidth=2, markersize=6, label='Precio')

# Graficar las líneas del canal
plt.plot(dates, linea_media_ajustada, 'b--', linewidth=1.5, label='Línea Media')
plt.plot(dates, linea_superior, 'r--', linewidth=1.5, label='Resistencia')
plt.plot(dates, linea_inferior, 'g--', linewidth=1.5, label='Soporte')

# Rellenar el canal entre soporte y resistencia
plt.fill_between(dates, linea_inferior, linea_superior, color='gray', alpha=0.2, label='Canal')

# Configuración del gráfico
plt.title('Evolución del Precio con Canal Paralelo Ajustado')
plt.xlabel('Fecha')
plt.ylabel('Precio ($)')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend()

# Mostrar el gráfico
plt.tight_layout()
plt.show()