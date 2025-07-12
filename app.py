import requests
import pandas as pd
import time

API_URL = "https://api.manarion.com/market"
ITEM_LIST_PATH = "ids.txt"


def load_list(path:str) -> dict[str,str]:
    try:
        with open(path, "r") as file:
            content = file.read().strip()
            if not content:
                return {}
            items = {}
            for pair in content.split(','):
                id, name = pair.split(':')[::-1]
                items[id] = name[1:-1]
            return items
    except FileNotFoundError:
        print(f"Error: The item list file was not found.")
    except Exception as e:
        print(f"An error occurred while loading the item list: {e}")


def fetch(url):
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching the data from API.\n",e)


items = load_list(ITEM_LIST_PATH)

data = fetch(API_URL)



# Creating a DataFrame

df = pd.DataFrame(columns=['Item', 'Profit %', 'Margin', 'BuyPrice', 'SellPrice'])
df['Item'] = [items[i] for i in items.keys() if i in data['Buy'] and i in data['Sell']]
df['BuyPrice'] = [data['Buy'][i] for i in items.keys() if i in data['Buy'] and i in data['Sell']]
df['SellPrice'] = [data['Sell'][i] for i in items.keys() if i in data['Buy'] and i in data['Sell']]
df.Item = df.Item.apply(lambda x: ''.join(y.capitalize() for y in x.split()))
df['Margin'] = df['SellPrice'] - df['BuyPrice']
df['Profit %'] = df['Margin'] * 100 / df['BuyPrice']  # Calculating Profit Percentage

# Sorting the DataFrame by Profit Percentage
df = df.sort_values(by='Profit %', ascending=False)
df.set_index('Item', inplace=True)
print(df.head(10))


items_camel = [''.join(word.capitalize() for word in item.split()) for key, item in items.items() if key in data['Buy']]
# print(items_camel)

big_boi_df = pd.DataFrame(columns=['TimeStamp']+[item+trade for item in items_camel for trade in ['Buy', 'Sell']])
TIMESTAMP = time.strftime("%Y-%m-%d %H:%M:%S")
big_boi_df.TimeStamp = [TIMESTAMP]
big_boi_df.set_index('TimeStamp', inplace=True)

for i in range(len(df)):
    item = df.index[i]
    big_boi_df[item+"Buy"] = df.iloc[i]["BuyPrice"]
    big_boi_df[item+"Sell"] = df.iloc[i]["SellPrice"]

