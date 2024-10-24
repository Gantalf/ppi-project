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

load_dotenv()

api_key = os.getenv('API_KEY')

ppi = PPI(sandbox=False)

# Letras - LECAP
# Calculo TNA
# Calculo TEA
# Calculo TEM
# graficar

ppi.account.login_api('c2ZHRVdOb1hLZHBHOUpMeDBpZFc=', api_key)

def get_historical_volume_data():
    historical_volume_data = ppi.marketdata.search(
        "SUPV", "Acciones", "A-24HS",
        datetime(2024, 1, 1),
        datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
    )
    return historical_volume_data

# Obtener los datos
info = get_historical_volume_data()

# Asegurar que las fechas sean objetos datetime y recopilar datos
dates = []
volumeValues = []
prices = []
colors = []
for data in info:
    volume = data['volume']
    date = parser.parse(data['date'])  # Convertir a datetime
    price = data['price']

    opening_price = data['openingPrice']
    if price > opening_price:
        colors.append('green')  # Más compras
    else:
        colors.append('red')

    dates.append(date)
    volumeValues.append(volume)
    prices.append(price)

# grafico volumen y precio

# Crear la figura y los ejes
fig, ax1 = plt.subplots(figsize=(12, 6))

# Graficar el volumen con barras de colores
ax1.bar(dates, volumeValues, color=colors, width=0.8, label='Volumen')
ax1.set_xlabel('Fechas')
ax1.set_ylabel('Volumen (Millones)', color='tab:blue')
ax1.grid(True)

# Formatear el eje Y para mostrar en millones
def millones(x, pos):
    return f'{x * 1e-6:.1f}M'
ax1.yaxis.set_major_formatter(FuncFormatter(millones))

# Formatear las fechas en el eje X
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)

# Crear un segundo eje Y para el precio
ax2 = ax1.twinx()
ax2.plot(dates, prices, color='tab:red', linestyle='--', linewidth=1, label='Precio')
ax2.set_ylabel('Precio ($)', color='tab:red')

# Agregar leyenda
fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

# Mostrar el gráfico
plt.tight_layout()
plt.show()








# Crear el gráfico solo volumen
# plt.figure(figsize=(10, 5))
# plt.plot(dates, volumeValues, marker='o', linestyle='-', linewidth=2, markersize=6)

# # Configuración del gráfico
# plt.title('Evolución del Volumen')
# plt.xlabel('Fechas')
# plt.ylabel('Volumen')
# plt.grid(True)

# # Rotar etiquetas del eje X y configurar los ticks de fechas
# plt.xticks(rotation=45)
# plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# def millons(x, pos):
#     """Función formateadora para mostrar en millones."""
#     return f'{x * 1e-6:.1f}M'

# plt.gca().yaxis.set_major_formatter(FuncFormatter(millons))
# # Ajustar los ticks del eje Y de forma más eficiente
# y_min = min(volumeValues) * 0.95  # Margen del 5% por debajo del mínimo
# y_max = max(volumeValues) * 1.05  # Margen del 5% por encima del máximo
# plt.ylim(y_min, y_max)  # Establece los límites del eje Y

# # Mostrar el gráfico sin solapamientos
# plt.tight_layout()
# plt.show()