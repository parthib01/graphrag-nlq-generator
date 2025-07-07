## 📁 Folder Structure
db/
├── create_tables.py # Python script for creating the tables.
├── insert_tables.py # Python script for adding rows to the tables.
├── retail.db # DB created after executing the .py files
├── schema.sql # schema of the database

1. create_tables.py
Creates a db - 'reail.db' if not present.
Drops the tables if already in db and creates them again.
Creates tables using SQL queries - Customer, Product, Orders, OrderItems, Store, Supplier, Rating. (refer schema.sql)

2. insert_tables.py
Connection is created to 'retail.db'.
The rows are added for each of the 7 tables using INSERT.

How to run:
1. Execute create_tables.py (python create_tables.py) --> 'retail.db' is created with tables.

2. Execute insert_tables.py (python insert_tables.py) --> tables are populated with data. 