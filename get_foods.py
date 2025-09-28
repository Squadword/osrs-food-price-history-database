import requests
import json

from db_query_function import db_query

# The URL for the mediawiki api of the osrs food table page, returning it in json format
url = "https://oldschool.runescape.wiki/api.php?action=query&prop=revisions&rvprop=content&titles=Food/All%20food&format=json"

# Some headers for the request so the wiki know who to contact if things get out of hand
headers = {
    'User-Agent': 'small home calculator - Discord: @Squadword ',
    'From': 'joshuaacbuck@gmail.com'
}

# Requesting the food data and loading it into a json
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# Extracting the table and removing some duplicate cell breaks
table = data['query']['pages']['366887']['revisions'][0]['*']
table = table.replace('\n\n', '\n')

# Splitting the table into rows
table = table.split('|-')

# Define empty lists for items we want to extract from the table
item_names = []
heal_amounts = []

# Loop through each row in the table
for i in table[1:]:

    # Seperate each item in the row
    i = i.split('\n')

    # Check if the item is tradeable, otherwise there will be no price for it
    if 'GEP' in i[5]:

        # Isolate the item name by getting the first item in the row then remove the padding
        name = i[1].split('|')[2][:].replace("}}", "" )
        
        item_names.append(name)

        # Extract the item that contains the heal amount
        heal_amount = i[2]

        # Some items heal varying amounts. If that is the case, we extract what is the highest possible amount
        if 'data-sort-value' in heal_amount:
            heal_amount = heal_amount[18:].split(' ')[0]

        # Otherwise we just extract the amount
        else:
            heal_amount = heal_amount.split('<')[0].split('|')[1:][0]

        heal_amounts.append(int(heal_amount))

# Now to map each item name to an item id number using the mapping api url
url = 'https://prices.runescape.wiki/api/v1/osrs/mapping'

# Request and load the data using the same headers as before
response = requests.get(url, headers=headers)
data = json.loads(response.text)

# Create a dictionary where each name maps to an id
item_id_index = {n['name']:n['id'] for n in data}

# Define an empty list for item ids
item_ids = []

# Loop through each item found from the food table
for item in item_names:

    # If we find the item in the dictionary, get the id and append it to the list
    if item in item_id_index:
        item_ids.append(item_id_index[item])

    # Otherwise we search through the dictionary for an item that contains the name ('strawberries' in food table is listed as 'strawberries(6)' in the mapping)
    else:
        temp = []
        for it in item_id_index:
            if item in it:
                temp.append(it)
                
        item_ids.append(item_id_index[temp[-1]])

# Here we double up any apostrophes (') in an item's name so that it can be parsed by an sql query later (e.g. Wizard's mind bomb --> Wizard''s mind bomb)
item_names = [i.replace("'", "''" ) for i in item_names]

# Reformat the data we have into a list of tuples rather than 3 seperate lists
items_data = [*zip(*[item_ids, item_names, heal_amounts])]

# Take our data and convert it to a string, removing the leading and ending '['.
data_for_query = str(items_data)[1:-1].replace('"', "'")

# Insert our data into the items table
# If the item is already in the table, we update its name and heal amount in case anything has changed since last time
db_query(f'''
    INSERT INTO items (item_id, item_name, heal_amount) 
    VALUES {data_for_query} 
    ON CONFLICT (item_id) 
    DO UPDATE SET
        item_name = EXCLUDED.item_name,
        heal_amount = EXCLUDED.heal_amount;
    ''')