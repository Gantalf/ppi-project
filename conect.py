from ppi_client.ppi import PPI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_KEY')

ppi = PPI(sandbox=False)

ppi.account.login_api('c2ZHRVdOb1hLZHBHOUpMeDBpZFc=', api_key)

# Getting accounts information
print("\nGetting instrument types")
instruments = ppi.configuration.get_instrument_types()

print(instruments)