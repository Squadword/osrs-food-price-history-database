
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

### The ```items``` table

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

### The ```item_prices``` table

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

This table would mostly work except for one major issue: a new entry to the table could be made for the same item on the same day. We want to avoid duplicate entries. Adding a combined unique constraint to the ```item_id``` and ```date``` columns solves this issue:

```SQL
ALTER TABLE item_prices
ADD UNIQUE (item_id, date);
```

Running this code results in the schema pictured below:

![image](https://github.com/Squadword/osrs-food-price-history-database/blob/main/imgs/Database%20schema.png)

# Populate the database
### Fill the items table

### Fill the item_prices table

# Analyse the data
