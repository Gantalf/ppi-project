from ppi_client.ppi import PPI
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import pytz
import numpy as np

load_dotenv()

api_key = os.getenv('API_KEY')

ppi = PPI(sandbox=False)

# Letras - LECAP
# Calculo TNA
# Calculo TEA
# Calculo TEM
# graficar

ppi.account.login_api('c2ZHRVdOb1hLZHBHOUpMeDBpZFc=', api_key)
argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')

tickers = [
    {"ticker": "S11N4", "vencimiento": "11/11/2024", "precio_estimado": 109.1 },
    {"ticker": "S12S5", "vencimiento": "12/9/2025", "precio_estimado": 158.98},
    {"ticker": "S13D4", "vencimiento": "13/12/2024", "precio_estimado": 126.83},
    {"ticker": "S14F5", "vencimiento": "14/2/2025", "precio_estimado": 121.24},
    {"ticker": "S14M5", "vencimiento": "14/3/2025", "precio_estimado": 125.96},
    {"ticker": "S16A5", "vencimiento": "16/4/2025", "precio_estimado": 131.21},
    {"ticker": "S16Y5", "vencimiento": "16/5/2025", "precio_estimado": 136.86},
    {"ticker": "S17E5", "vencimiento": "17/1/2025", "precio_estimado": 131.185},
    {"ticker": "S18J5", "vencimiento": "18/6/2025", "precio_estimado": 147.7},
    {"ticker": "S28F5", "vencimiento": "28/2/2025", "precio_estimado": 158.2875},
    {"ticker": "S29G5", "vencimiento": "29/8/2025", "precio_estimado": 157.7},
    {"ticker": "S29N4", "vencimiento": "29/11/2024", "precio_estimado": 134.9833},
    {"ticker": "S30J5", "vencimiento": "30/6/2025", "precio_estimado": 146.61},
    {"ticker": "S31E5", "vencimiento": "31/1/2025", "precio_estimado": 172.6534},
    {"ticker": "S31M5", "vencimiento": "31/3/2025", "precio_estimado": 155.5815},
]

colors = plt.cm.get_cmap('tab20b_r', len(tickers))
final_tem_values = []

for i, ticket in enumerate(tickers):
   try:
        instrument = ppi.marketdata.search(ticket["ticker"], "LETRAS", "A-24HS", datetime(2021, 1, 1), datetime.now())
       
        dates = []
        yields = []
        temValues = []
        

        finishedDateStr = ticket["vencimiento"]
        finishedDate = argentina_tz.localize(datetime.strptime(finishedDateStr, '%d/%m/%Y'))
        

        for data in instrument:
                
                currentDate = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S%z').astimezone(argentina_tz)
                CurrentPrice = data['price']  # Precio actual

                #calculated_yield = (ticket["precio_estimado"] - CurrentPrice) / CurrentPrice * 100 <-- TE

                #TEM
                days_to_maturity = (finishedDate - currentDate).days
                #TEA
                teaCalc = (ticket["precio_estimado"] / CurrentPrice) ** (365 / days_to_maturity) - 1
                #TEM
                temCalc = (1 + teaCalc) ** (1 / 12) - 1 

                #print(f"Fecha: {currentDate} - Precio: {CurrentPrice} - TEA: {teaCalc * 100} - TEM: {temCalc * 100}")
                dates.append(currentDate)
                #yields.append(calculated_yield)
                temValues.append(temCalc * 100)

        plt.scatter(dates, temValues, label=ticket["ticker"], color=colors(i))

        final_tem_values.append([ticket["ticker"], f'{temValues[-1]:.2f}%'])

   except Exception as e:
       print(f"Error al buscar el ticket {ticket}: {e}")

plt.xlabel("Fecha")
plt.ylabel("TEM (%)")
plt.title("TEM de LECAPs a lo largo del tiempo")
plt.legend()

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=10))  
plt.gcf().autofmt_xdate(rotation=45)  


def format_y_ticks(value, pos):
    return f'{value:.2f}'  

plt.gca().yaxis.set_major_formatter(FuncFormatter(format_y_ticks))
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))  

plt.xlim([datetime(2024, 3, 14), datetime.now()])

# tabla 
column_labels = ["Ticker", "Último TEM (%)"]
table = plt.table(cellText=final_tem_values, colLabels=column_labels, loc='center right', colWidths=[0.15, 0.15], cellLoc='center', bbox=[1.05, 0, 0.3, 1])
table.auto_set_font_size(False)  
table.set_fontsize(10)

plt.subplots_adjust(right=0.75)

plt.legend()

plt.show()