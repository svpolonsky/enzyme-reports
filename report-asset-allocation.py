# Report on Asset Allocation and how it compares with target

# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd

pd.set_option('display.float_format', '{:.2f}'.format)
load_dotenv()

# URL for the request
url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultPortfolio"

# Headers to be sent with the request
ENZYME_API_KEY=os.getenv('ENZYME_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ENZYME_API_KEY}",
    "Connect-Protocol-Version": "1"
}

# Data to be sent in JSON format
address = os.getenv('ENZYME_VAULT_ADDRESS')
data = {
  "deployment": "DEPLOYMENT_UNSPECIFIED",
  "address": address,
  "currency": "CURRENCY_UNSPECIFIED"
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# convert json to pandas dataframe


assets = pd.DataFrame(response.json()["assets"])


# Coin Name - specific coin name 
# Asset Name - few coins can contribute to the same asset (e.g. WBTC and renBTC both contribute to BTC)
coin_data = {
     
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": {
          "Coin Name": "WBTC",
         "Asset Name": "BTC",
        "Asset Class": "Native Coins"
    },

    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
          "Coin Name": "WETH",
         "Asset Name": "ETH",
        "Asset Class": "Native Coins"
    },

    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": { 
          "Coin Name": "stETH",
         "Asset Name": "ETH",
        "Asset Class": "Native Coins"
    },

    "0xd31a59c85ae9d8edefec411d448f90841571b89c" : {
          "Coin Name": "WSOL",
         "Asset Name": "SOL",
        "Asset Class": "Native Coins"
    },

    "0xdac17f958d2ee523a2206206994597c13d831ec7": {
          "Coin Name": "USDT",
         "Asset Name": "USDT",
        "Asset Class": "Stable Coins"
    },

    "0x23878914efe38d27c4d67ab83ed1b93a74d4086a": {
            "Coin Name": "aEthUSDT", 
             "Asset Name": "USDT",
            "Asset Class": "Stable Coins"
    },

    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": {
          "Coin Name": "USDC",
         "Asset Name": "USDC",
        "Asset Class": "Stable Coins"
    },

    "0x6b175474e89094c44da98b954eedeac495271d0f": {
          "Coin Name": "DAI",
         "Asset Name": "DAI",
        "Asset Class": "Stable Coins"
    },

    "0x018008bfb33d285247a21d44e50697654f754e63": {
          "Coin Name": "aEthDAI",
         "Asset Name": "DAI",
        "Asset Class": "Stable Coins"
    },

    "0xec67005c4e498ec7f55e092bd1d35cbc47c91892": {
          "Coin Name": "MLN",
         "Asset Name": "MLN",
        "Asset Class": "Internal"
    },
}

# add a new column to the dataframe by mapping address to the coin_data dictionary's Coin Name
assets["Coin Name"] = assets["address"].map(lambda x: coin_data[x]["Coin Name"])
# add a new column to the dataframe by mapping address to the coin_data dictionary's Asset Name
assets["Asset Name"] = assets["address"].map(lambda x: coin_data[x]["Asset Name"])
# add a new column to the dataframe by mapping address to the coin_data dictionary's Asset Class
assets["Asset Class"] = assets["address"].map(lambda x: coin_data[x]["Asset Class"])
# delete the address column
del assets["address"]

# pretty print the dataframe
#print(assets)

# calculate the total value of the assets
total_value = assets["value"].sum()
print(f"\nTotal Value: {total_value:.2f}")

# calculate the total value of the assets by asset class
assets_by_class = assets.groupby('Asset Class').sum() 
# keep only these columns
assets_by_class.drop(assets_by_class.columns.difference(['value', 'Asset Class']), axis=1, inplace=True)
# add a new column to the dataframe with the percentage of the total value
assets_by_class["Percentage"] = assets_by_class["value"] / total_value * 100
print(f'\nAssets by class:')
print(assets_by_class)


def report_inclass_allocations(index_csv, assets, class_name='Native Coins'):
    print(f'\nInclass allocations for {class_name}:')
    # keep rows with Asset Class = class_name
    coins = assets[assets["Asset Class"] == class_name]
    # aggregate the values by Asset Name
    inclass_assets = coins.groupby('Asset Name').sum()
    # add a new column to the dataframe with the percentage of the total value
    inclass_assets["Percentage"] = inclass_assets["value"] / assets_by_class["value"][class_name] * 100
    # keep only these columns
    inclass_assets.drop(inclass_assets.columns.difference(['Asset Name', 'value', 'Percentage']), axis=1, inplace=True)
    # manual download https://www.coindesk.com/indices
    index = pd.read_csv(index_csv, usecols=['Symbol', 'Weight'], dtype={'Weight': float})
    # uppercase the Symbol column
    index['Asset Name'] = index['Symbol'].str.upper()
    # Add Reference column
    inclass_assets = inclass_assets.merge(index[['Asset Name', 'Weight']], on='Asset Name', how='left')
    inclass_assets.rename(columns={'Weight': 'Reference'}, inplace=True)
    # in-place sort by Percentage
    inclass_assets.sort_values(by='Percentage', ascending=False, inplace=True)
    # inclass_assets.style.format({
    #     'value': '{:.2f}',
    #     'Percentage': '{:.2f}',
    #     'Reference': '{:.2f}'
    # })
    
    # df['A'] = df['A'].map('{:.2f}'.format)
    print(inclass_assets.to_string(index=False))

report_inclass_allocations('Constituents - CoinDesk Large Cap Select Index.csv', assets, 'Native Coins')
report_inclass_allocations('Constituents - CoinDesk Stablecoin Index.csv', assets, 'Stable Coins')