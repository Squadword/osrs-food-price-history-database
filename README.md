
# Table of Contents

- [Overview](#overview)
- [Create the database](#create-the-database)
  - [items table](#the-items-table)
  - [item_prices table](#the-item_prices-table)
- [Populate the database](#populate-the-database)
  - [Fill the items table](#fill-the-items-table)
  - [Fill the item_prices table](#fill-the-item_prices-table)
  - [Automating data transfer](#automating-data-transfer)
- [Analyse the data](#analyse-the-data) 
  - [Power BI](#power-bi)
  - [Python](#python)
- [Reflection](#reflection)
  - [Learnings](#learnings)
  - [Improvements and Extensions](#improvements-and-extensions)

# Overview

In the game Old School Runescape (OSRS), your player has a health bar. This can be refilled by eating food ([list of all foods](https://oldschool.runescape.wiki/w/Food/All_food)), for example a lobster heals your character for 12 hitpoints (HP):

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/Lobster%20eat%20screenshot.png)

Additionally, OSRS contains a player to player auction house called The Grand Exchange (GE). Items can be sold and bought asynchronously, with players setting a price then their buy/sell order being fulfilled when somebody matches their offer.

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/GE%20screenshot.png)

Websites such as the [OSRS wiki prices page](https://prices.runescape.wiki/osrs/item/379) have created ways for players to track the average prices of items. 

The goal of this project is to create my own database, storing the historical prices of all tradeable foods in OSRS, so that I can find the cheapest way to heal myself in game.

# Create the database

To store data about the items and their prices, we need to create a simple database. I used [Supabase](https://supabase.com/) as their free tier is generous and allows for external connections. The database will have 2 tables, 1 for storing information about each item, this will be the items table. And the other for storing the price history of these items, this will be the item_prices table.

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

## Fill the items table

This step primarily uses the [```get_foods.py```](get_foods.py) and [```db_query_function.py```](db_query_function.py) scripts.

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

Once the item names, ids, and heal amounts were found it was time to upload them to the table. To connect to the database, I used the [psycopg2](https://pypi.org/project/psycopg2/) package and created a function to interface with the database in [```db_query_function.py```](db_query_function.py). As the ```item_ids``` column in the ```items``` table has a constraint of UNIQUE, it is sensible to set up instructions for what to do ON CONFLICT. Updating the data is sensible as there could be updates to the game in the future that change an items ```heal_amount```. We can then call the query in python, where ```data_for_query``` is string of tuples containing all the data.

```SQL
INSERT INTO items (item_id, item_name, heal_amount) 
VALUES {data_for_query} 
ON CONFLICT (item_id) 
DO UPDATE SET
item_name = EXCLUDED.item_name,
heal_amount = EXCLUDED.heal_amount;
```

After uplading we can check the data by either performing a ```SELECT``` statement or using the GUI on supabase. All looks good:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/items%20table.png)

## Fill the item_prices table

This step primarily uses the [```get_food_prices.py```](get_food_prices.py) and [```db_query_function.py```](db_query_function.py) scripts.

To fill the  ```item_prices``` table we need to find 3 data points: an item, its price, and the date at which it was that price. The ```items``` table holds all the items we would be interested in so it makes sense to first get a list of all the item ids from that table:

```SQL
SELECT item_id FROM items;
```

Once a list of items is obtained, the prices for these items needs to be found. The [OSRS wiki](https://oldschool.runescape.wiki/) has a [real time prices api](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices) where endpoints return varying information about items' prices. Using the [timeseries endpoint](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices#Time-series) returns historical data for the item queried that can go back as far as 365 days. Looping through the items obtained from the ```items``` table, we can find 365 data points per item that would be useful to have in the database. After extracting every date and price for each item, the data needs reformatting and can then be uploaded to the database using the query below, where ```data_for_query``` is string of tuples containing all the data. As the data is historical, there is no need to UPDATE ON CONFLICT as the data should never be changing.

```SQL
INSERT INTO item_prices (item_id, date, price) 
VALUES {data_for_query}
ON CONFLICT DO NOTHING;
```

After uplading we can check the data by either performing a ```SELECT``` statement or using the GUI on supabase. An interesting anomaly presents itself:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/item%20prices%20table.png)

We can see there is data from significantly longer than 365 days ago which is odd as the api specifies 365 days of data. Taking item id number 5929 for example we can match it using the wiki's [item  id table](https://oldschool.runescape.wiki/w/Item_IDs) and find that it is an obscure item called 'Cider(m4)'. using the market watch graph on the [item's wiki page](https://oldschool.runescape.wiki/w/Cider(m)_(keg)#4_pints) shows that the trade volume is frequently incredibly low, meaning there are likely days where 0 items are bought/sold:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/cider%20graph.png)

This means the api is most likely skipping over days where it has no data for the prices items traded and is instead returning older data. Otherwise, looking through the data, all seems good.

## Automating data transfer

In order to automate the filling of data into the database, the scripts [```get_foods.py```](get_foods.py) and [```get_food_prices.py```](get_food_prices.py) scripts need to be run automatically at set intervals. This could simply be done locally on a windows machine using something like [Windows Task Schedular](https://en.wikipedia.org/wiki/Windows_Task_Scheduler) or alternatively, the scripts could be hosted. For example sitting in something like an [AWS Lambda](https://aws.amazon.com/lambda/) or on a service such as [Python Anywhere](https://www.pythonanywhere.com/).

The [```get_foods.py```](get_foods.py) script would not need to be run very frequently, as foods are not often added to the game, and changes to their properties are very rare. So the script could run as rarely as monthly, or if incredibly accurate data is vital, the script could be run weekly, potentially a day or 2 after the weekly update.

The [```get_food_prices.py```](get_food_prices.py) script would need to run more frequently, as the price data updates every day. Personally, I would not run the script more than weekly, as I am not interested in exactly current data, but there could be applications where this script needs running daily.

For my purposes though, I simply run the scripts whenever I want to do some analysis, so I know I have up to date data.

# Analyse the data

While analysis was not the focus of this project, we can do some light analysis in to show possible applications of the data.

### Power BI

We can make an ugly dashboard in Power BI. First the data needs to be imported which can be done directly using Power BI's inbuilt PostgreSQL database connection.

Next we can start by creating a table of all foods and how much they heal. We can then add the price of the item, filtering by the most recent date. Then we can create a quick measure dividing the heal amount by the current cost to get a price per heal, showing how cost effective a food is. Finally, we can add a slider to filter foods by the amount they heal:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/table%20data.png)

Using the slider to only show foods that heal above 20 HP, we can see a table of the highest healing food in the game. We would expect these to be high priority for high level players, as inventory space is limited and they would want to bring as much healing as possible to a fight. Sorting by GP/Heal shows the most cost effective foods that heal over 20 and strawberries are the clear winner here. However, in general, the most popular foods for healing in combat in the game are manta rays, dark crabs, and tuna potato even though they score lower down on the list. To find out why, we can look further into some of the items that score well. Doing some investigation on the [wiki page for strawberries](https://oldschool.runescape.wiki/w/Strawberries#(5)), we can see that this item comes as a basket of 5 individual strawberries, meaning that in order for the player to get the full healing effect of 30 HP, they would have to click and eat the basket of strawberries 5 times and spend more time eating than other foods on this list. This makes them and inconvenient food when compared to other alternatives. Other foods on this list suffer from the same issue. All pies and pizzas require multiple bites to get the full effect, so are less time efficient than the single bite counter parts.


To analyse more than just foods at their current prices, we can create a graph to show price history. Adding a word filter and a multiple selection filter allows for only having a few items on the graph. Filtering for the three most popular foods (manta rays, dark crabs, and tuna potato) shows a timeseries of these foods' price in the past year:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/graph%20data.png)

Looking at the graph we can see that manta rays are generally more expensive than the other two items, particularly between July and September 2025. Tuna potatoes had a strange event at the end of July where price more than doubled. Sudden increases like this are potentially due to either a group of players [merching](https://oldschool.runescape.wiki/w/Merchanting) or a significant number of [bots](https://oldschool.runescape.wiki/w/Botting) being banned.

### Python


# Reflection

### Learnings

- Importing and transforming data from the wikimedia api.
  - This was harder than expected due to the awkward formatting of the wikitable object.
- Creating a database from scratch in SupaBase.
  - This was simple and the gui made everything easy to check along the way.
- Using the psycopg2 package to interface with a database through Python.
- Directly connecting a database to PowerBI.

### Improvements and Extensions

- Extending the data in the database to store number of bites it takes to eat a food. As mentioned in the [Power BI](#power-bi) section, it is an important factor to consider when looking at what foods players prioritise.
- Expand the database to other items such as potions. This would require working with additional pages on the runescape wiki but would allow for other analyses such as checking the price efficiency of training certain skills.
- Rewrite the wiki api ingestion code to be more general. As the wikitable format was awkward to work with, the code I wrote was not very versatile and was hard coded in parts. Rewriting it to be more widely applicable would allow extensions like the previous point to be carried out more easily.
  


