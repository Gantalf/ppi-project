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

ppi.account.login_api('c2ZHRVdOb1hLZHBHOUpMeDBpZFc=', api_key)

def get_current_book():
    current_book = ppi.marketdata.book(
        "METR", "Acciones", "A-24HS",
    )

    return current_book

# Obtener los datos
info = get_current_book()
print(info)
bids = info["bids"]
offers = info["offers"]

# Determinar el mejor bid (máximo precio de compra)
best_bid = max(bids, key=lambda x: x['price'])

# Determinar el mejor offer (mínimo precio de venta)
best_offer = min(offers, key=lambda x: x['price'])

print(f"Mejor bid: {best_bid} - Mejor offer: {best_offer}")

if best_bid['price'] >= best_offer['price']:
    print(f"Hay una oportunidad de arbitraje con un spread de {best_bid['price'] - best_offer['price']}")
else:
    print("No hay oportunidad de arbitraje")