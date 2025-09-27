import requests
import json
import datetime

from db_query_function import db_query

# Extract a list of the item ids from the items table 
item_ids = db_query(f'''
    SELECT item_id FROM items;
    ''') 


# Some headers for the request so the osrs wiki know who to contact if things get out of hand
headers = {
    'User-Agent': 'small home calculator - Discord: @Squadword ',
    'From': 'joshuaacbuck@gmail.com'
}

# Define an empty list to contain the price history for each item
items_price_data = []

# Loop through each item
for id in item_ids:

    # Query the wiki api for the item's price history and load into a json
    url = f"https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep=24h&id={id[0]}"
    response = requests.get(url, headers=headers)
    price_history_json = json.loads(response.text)

    # Define empty lists for the dates and prices
    item_dates = []
    item_prices = []

    # Loop through each point in time
    for t in price_history_json['data']:

        # Convert the timestamp to a string and add to the dates list
        date = datetime.datetime.fromtimestamp(t['timestamp'])
        date_string = f'{date.year}-{date.month}-{date.day}'
        item_dates.append(date_string)

        # Add the price to the prices list
        item_prices.append(t['avgHighPrice'])

        # Convert the 2 lists into a list of tuples so it is ready for the SQL query later
        item_price_log = [*zip(*[[id[0]]*len(item_dates), item_dates, item_prices])]

    # Add the item's price history to the main list
    items_price_data += item_price_log

# Convert the data to a string and replace the None values as the database takes NULL instead
string_for_query = str(items_price_data)[1:-1].replace('None', 'NULL')

# Insert the data into the item_prices table
# There is no need to update on conflict as the data is historical and should never change
db_query(f'''
    INSERT INTO item_prices (item_id, date, price) 
    VALUES {string_for_query}
    ON CONFLICT DO NOTHING;
    ''')

