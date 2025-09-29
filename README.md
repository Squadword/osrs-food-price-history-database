
# Table of Contents

- [Overview](#overview)
- [Create the database](#create-the-database)
  - [items table](#items-table)
  - [item_prices table](#item_prices-table)
- [Populate the database](#populate-the-database)
  - [Fill the items table](#fill-the-items-table)
  - [Fill the item_prices table](#fill-the-item_prices-table)
- [Analyse the data](#analyse-the-data) 

# Overview

In the game Old School Runescape (OSRS), your player has a health bar. This can be refilled by eating food ([list of all foods](https://oldschool.runescape.wiki/w/Food/All_food)), for example a lobster heals your character for 12 hitpoints (HP):

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/Lobster%20eat%20screenshot.png)

Additionally, OSRS contains a player to player auction house called The Grand Exchange (GE). Items can be sold and bought asynchronously, with players setting a price then their buy/sell order being fulfilled when somebody matches their offer.

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/GE%20screenshot.png)

Websites such as the [OSRS wiki prices page](https://prices.runescape.wiki/osrs/item/379) have created ways for players to track the average prices of items. 

The goal of this project is to create my own database, storing the historical prices of all tradeable foods in OSRS, so that I can find the cheapest way to heal myself in game.

# Create the database

To store data bout the items and their prices, we need to create a simple database. I used [Supabase](https://supabase.com/) as their free tier is generous and allows for external connections. The database will have 2 tables, 1 for storing information about each item, this will be the items table. And the other for storing the price history of these items, this will be the item_prices table.

## The ```items``` table

The items table will contain 3 columns:

- ```item_name```, a text column containing the name of the food.
- ```item_id```, a unique integer for each item, and the primary key of the table. Items in OSRS already come with a unique item id so we can use those.
- ```heal_amount```, an integer column containing the amount of HP that each food heals.

This table can be created with the code below:

```SQL
CREATE TABLE items (
  item_id INT NOT NULL UNIQUE PRIMARY KEY,
  item_name TEXT NOT NULL,
  heal_amount INT NULL,
);
```

## The ```item_prices``` table

The ```item prices``` table will be more complex than the ```items``` table, and contain 4 columns:

- ```price_id```, an integer column that generates a unique id for each entry to the table. This will be the primary key.
- ```item_id```, a foreign key to the ```items``` table.
- ```price```, an integer column to record the price of an item at a certain date.
- ```date```, a date column for the date that the price was recorded at.

This table can be created with the code below:

```SQL
CREATE TABLE item_prices (
  price_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  item_id INT NOT NULL REFERENCES items (item_id),
  price INT NULL,
  date DATE NOT NULL
);
```

This table would mostly work except for one major issue: a new entry to the table could be a duplicate entry. We can adding a combined unique constraint to the ```item_id``` and ```date``` columns to solve this issue:

```SQL
ALTER TABLE item_prices
ADD UNIQUE (item_id, date);
```

Running this code results in the schema pictured below:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/Database%20schema.png)

# Populate the database

### Fill the items table

This step primarily uses the [```get_foods.py```](get_foods.py) and [```db_query_function.py```](db_query_function.py) script.

The first step to filling the databse with data is to find a collection of all the foods. Fortunately the [OSRS Wiki](https://oldschool.runescape.wiki/) is an incredibly useful resource and runs on [MediaWiki](https://www.mediawiki.org/wiki/MediaWiki), which has a comprehensive [API](https://www.mediawiki.org/wiki/API:Action_API). The wiki has a page called [All Food](https://oldschool.runescape.wiki/w/Food/All_food) which contains a collection of all foods in the game and additional information about them, notably the healing amount. Using a technique outlined by [OSRS Box](https://www.osrsbox.com/blog/2018/12/12/scraping-the-osrs-wiki-part1/), we can scrape this page of the wiki and start working with the table in Python. Unfortunately, the result is an awkward object called a wikitable that looks like:

```
['{| class="wikitable sortable sticky-header align-center-1 align-right-6 align-right-7"\n! colspan=2 |Food\n!Heals<ref>healing is shown as [per bite × total bites] for foods with multiple bites</ref>\n! data-sort-type=number |Skill(s)<br/>Needed\n!Notes\n! data-sort-type=number |GP per heal<ref>GP per heal on food that take multiple bites indicate the total hp healed, rather than per bite or dose.</ref>\n! data-sort-type=number |Price\n!Members\n',
 '\n|{{plinkt|Cup of tea}}\n|3\n|{{SCP|Thieving|5}}\n|Boosts Attack by 2% + 2{{fact}}\n|{{Coins|{{GEP|Cup of tea}}/3}}\n|{{Coins|{{GEP|Cup of tea}}}}\n|{{members|Yes}}\n',
 "\n|{{plinkt|Bruised banana}}\n|0\n|\n|Taken from the  [[spooky cauldron]] behind [[Zaff's Superior Staves]]. It was used in the [[2022 Halloween event|2022]] and [[2023 Halloween event|2023 Halloween events]].\n|{{NA}}\n|{{NA}}\n|{{members|No}}\n",
 '\n|{{plinkt|Tea flask}}\n| data-sort-value=15 |3 × 5\n|\n|Reusable item obtained via [[Creature Creation]]<br/>Must be filled with Cups of tea<br/>Boosts Attack by 3{{fact}}\n|{{NA}}\n|{{NA}}\n|{{members|Yes}}\n',
 '\n|{{plinkt|Poison chalice}}\n| data-sort-value=-1 |Random\n|\n|Has a chance to apply a variety of random effects which can be beneficial or harmful<br/>Has a chance to either heal or severely harm the player\n|{{Coins|{{GEP|Poison chalice}}/14}} – {{Coins|{{GEP|Poison chalice}}}}\n|{{Coins|{{GEP|Poison chalice}}}}\n|{{members|Yes}}\n',
 '\n|{{plinkt|Caerula berries}}\n|2\n|\n|Found in [[Caerula bush]]es, found north of the [[Twilight Temple]]\n|{{NA}}\n|{{NA}}\n|{{members|Yes}}\n',
 '\n|{{plinkt|Jangerberries}}\n|2\n|\n|\n|{{Coins|{{GEP|Jangerberries}}/2}}\n|{{Coins|{{GEP|Jangerberries}}}}\n|{{members|Yes}}\n',
...
...
```

There are packages designed for parsing responses from the MediaWiki API such as [mwparserfromhell](https://mwparserfromhell.readthedocs.io/en/latest/), however, it is fairly straightforward to split the data then extract the necessary parts. The main problems arise from items that heal varying amounts. For these, the highest possible amount healed was extracted.

Next, each item had to be mapped to its unique id. Using the OSRS wiki [prices API](https://prices.runescape.wiki/api/v1/osrs/mapping)'s endpoint called [mapping](https://prices.runescape.wiki/api/v1/osrs/mapping) the names of each item were matched to its id. There were some issues with items such as [saradomin brew](https://oldschool.runescape.wiki/w/Saradomin_brew#4_dose) that have multiple variations, so the highest healing variant was chosen.

Once the item names, ids, and heal amounts were found it was time to upload them to the table. To connect to the database, I used the [psycopg2](https://pypi.org/project/psycopg2/) package and created a function to interface with the database in [```db_query_function.py```](db_query_function.py). As the ```item_ids``` column in the ```items``` table has a constraint of UNIQUE, it is sensible to set up instructions for what to do ON CONFLICT. Updating the data is sensible as there could be updates to the game in the future that change an items ```heal_amount```. We can then call the query in python, where ```data_for_query```, is string of tuples containing all the data.

```Python
db_query(f'''
    INSERT INTO items (item_id, item_name, heal_amount) 
    VALUES {data_for_query} 
    ON CONFLICT (item_id) 
    DO UPDATE SET
        item_name = EXCLUDED.item_name,
        heal_amount = EXCLUDED.heal_amount;
    ''')
```

After uplading we can check the data by either performing a ```SELECT``` statement or using the GUI on supabase. All looks good:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/items%20table.png)

### Fill the item_prices table



# Analyse the data


