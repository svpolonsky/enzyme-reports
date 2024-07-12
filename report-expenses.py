import shelve
import sys
from moralis import evm_api
import json
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import requests
from prettytable import PrettyTable

def normalize_date(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_date = datetime_obj.strftime('%d-%m-%Y')
    return formatted_date

class EthereumHistoricPrice:
    def __init__(self, currency="usd"):
        self.db = shelve.open("prices", writeback=True) 
        self.currency = currency
        self.api_key = os.getenv('COINGECKO_API_KEY')

    def __del__(self):
        # print("Closing Prices database")
        self.db.close()

    def quote(self, date):
        if date in self.db:
            # print(f"Retrieving {date} from cache")
            pass
        else:
            url = f"https://api.coingecko.com/api/v3/coins/ethereum/history?date={date}&localization=false"
            headers = {"accept": "application/json","x-cg-api-key": self.api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.db[date] = response.json()
                self.db.sync()
                print(f"Retrieved {date} from API")
            else:
                print(f"Failed to retrieve {date} from API")
                return None
        return self.db[date]["market_data"]["current_price"][self.currency]
    
class TradesData:
    def __init__(self):
        self.db = shelve.open("trades") 
        self.api_key = os.getenv('MORALIS_API_KEY')

    def __del__(self):
        # print("Closing Trades database")
        self.db.close()

    def qet(self, transaction_hash):
        if transaction_hash in self.db:
            # print('Transaction already exists')
            pass
        else:
            # print('Transaction does not exist, adding it to the shelve')
            params = {"chain": "eth", "transaction_hash": transaction_hash}
            result = evm_api.transaction.get_transaction(api_key=self.api_key,params=params)
            self.db[transaction_hash] = result
            self.db.sync()
            # I use free API, so I need to wait in case throughput limits are reached
            time.sleep(1)
        return self.db[transaction_hash]
        
load_dotenv()

# Initialize locally cached obbjects
price_usd = EthereumHistoricPrice("usd")
trade = TradesData()

# get filename from command line argument, if not provided, use default
filename = sys.argv[1] if len(sys.argv) > 1 else 'vault-activity.json'


with open(filename, 'r') as file:
    data = json.load(file)

def get_part_before_slash(s):
    return s.split('/')[0]



# Create a table object
table = PrettyTable()
table.field_names = ["Date", "Fee (USD)"]

def trade_fee(transaction_hash,table):
    t = trade.qet(transaction_hash)
    fee_eth = float(t["transaction_fee"])
    block_date = normalize_date(t["block_timestamp"])
    eth_price = price_usd.quote(block_date)
    fee_usd = fee_eth * eth_price
    print(f'Date  {block_date} Fee (USD): {fee_usd}' )
    table.add_row([block_date, "{:.2f}".format(fee_usd)])
    
for activity in data['vaultActivities']:
    if 'trade' in activity:
        transaction_hash = get_part_before_slash(activity['trade']['id'])
        print(f'Trade {transaction_hash}')
        trade_fee(transaction_hash, table)

print(table)

    