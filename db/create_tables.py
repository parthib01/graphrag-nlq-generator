import sqlite3

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect('retail.db')

# Enable foreign key enforcement (must do this per connection) :contentReference[oaicite:2]{index=2}
conn.execute("PRAGMA foreign_keys = ON;")

cursor = conn.cursor()

# Drop tables if they exist (helps when running script multiple times)
tables = ["Review", "OrderItem", "Orders", "Store", "Product", "Supplier", "Customer"]
for tbl in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {tbl};")

# 1. Customer table
cursor.execute("""
CREATE TABLE Customer (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    phone_number  TEXT    NOT NULL
);
""")

# 2. Supplier table
cursor.execute("""
CREATE TABLE Supplier (
    supplier_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    region        TEXT
);
""")

# 3. Product table with FK to Supplier
cursor.execute("""
CREATE TABLE Product (
    product_id   INTEGER PRIMARY KEY,
    name         TEXT    NOT NULL,
    category     TEXT,
    brand        TEXT,
    price        REAL    NOT NULL,
    supplier_id  INTEGER NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);
""")

# 4. Store table
cursor.execute("""
CREATE TABLE Store (
    store_id   INTEGER PRIMARY KEY,
    location   TEXT,
    region     TEXT,
    type       TEXT
);
""")

# 5. Order table with FKs
cursor.execute("""
CREATE TABLE Orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL,
    store_id      INTEGER,
    order_date    TEXT    NOT NULL,
    total_amount  REAL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (store_id)    REFERENCES Store(store_id)
);
""")

# 6. OrderItem junction table
cursor.execute("""
CREATE TABLE OrderItem (
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL    NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id)   REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);
""")

# 7. Review table
cursor.execute("""
CREATE TABLE Review (
    review_id    INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_date  TEXT    NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (product_id)  REFERENCES Product(product_id)
);
""")



# Commit schema changes
conn.commit()
print("Tables successfully created in retail.db")

conn.close()
