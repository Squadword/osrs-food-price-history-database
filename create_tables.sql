CREATE TABLE items (
  item_id INT NOT NULL UNIQUE PRIMARY KEY,
  item_name TEXT NOT NULL,
  heal_amount INT NULL,
);

CREATE TABLE item_prices (
  price_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  item_id INT NOT NULL REFERENCES items (item_id),
  price INT NULL,
  date DATE NOT NULL
);

ALTER TABLE item_prices
ADD UNIQUE (item_id, date);