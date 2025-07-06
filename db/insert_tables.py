import sqlite3

# 1. Connect to SQLite with foreign keys enabled
conn = sqlite3.connect('retail.db')
conn.execute("PRAGMA foreign_keys = ON;")

with conn:  # ensures commit/rollback automatically :contentReference[oaicite:4]{index=4}
    # Insert Customers
    customers = [
        (1001, 'Alice Sharma', 'alice.sharma@example.com', '987xxxx210'),
        (1002, 'Ravi Kumar',   'ravi.kumar@example.com',   '912xxxx780'),
        (1003, 'Priya Nair',   'priya.nair@example.com',   '998xxxx655'),
        (1004, 'Arun Menon',   'arun.menon@example.com',   '900xxxx334')
    ]
    conn.executemany("""
        INSERT INTO Customer (customer_id, name, email, phone_number) 
        VALUES (?, ?, ?, ?)""", customers)

    # Insert Suppliers
    suppliers = [
        (2001, 'Global Textiles Co.', 'Kerala'),
        (2002, 'Vasthra Textiles Co.', 'Rajasthan'),
        (2003, 'Acme Electronics', 'Karnataka'),
        (2004, 'Light Electronics', 'Maharashtra'),
        (2005, 'Fresh Foods Ltd.', 'Tamil Nadu'),
        (2006, 'Tripthi Foods Ltd.', 'Tamil Nadu')
    ]
    conn.executemany("""
        INSERT INTO Supplier (supplier_id, name, region)
        VALUES (?, ?, ?)""", suppliers)

    # Insert Products
    products = [
        (3001, 'Cotton T-Shirt', 'Apparel', 'GTC', 450.00, 2001),
        (3002, 'Silk Saree', 'Apparel', 'GTC', 1785.00, 2001),
        (3003, 'Jeans', 'Apparel', 'GTC', 650.00, 2002),
        (3004, 'Bluetooth Headphones', 'Electronics', 'SoundPro', 1600.00, 2003),
        (3005, 'Laptop', 'Electronics', 'Lenovo', 48000.00, 2004),
        (3006, 'Mobile Phone', 'Electronics', 'Samsung', 35500.00, 2003),
        (3007, 'Organic Honey 500g', 'Grocery', 'BeePure', 500.00, 2005),
        (3008, 'Tea powder', 'Grocery', 'Brooke Bond', 120.00, 2005),
        (3009, 'Biscuits', 'Grocery', 'Britannia', 70.00, 2006)
    ]
    conn.executemany("""
        INSERT INTO Product (product_id, name, category, brand, price, supplier_id)
        VALUES (?, ?, ?, ?, ?, ?)""", products)

    # Insert Stores
    stores = [
        (4001, 'MG Road, Kochi', 'Kochi', 'Retail Outlet'),
        (4002, 'Jayanagar, Bangalore', 'Bangalore', 'Retail Outlet'),
        (4003, 'T Nagar, Chennai', 'Chennai',   'Retail Outlet'),
        (4004, 'Chandwaji Road, Jaipur', 'Jaipur', 'Retail Outlet'),
        (4005, 'Jayant Road, Mumbai', 'Mumbai', 'Retail Outlet')
    ]
    conn.executemany("""
        INSERT INTO Store (store_id, location, region, type)
        VALUES (?, ?, ?, ?)""", stores)

    # Insert Orders
    orders = [
        (5001, 1001, 4001, '2024-06-10', 2685.00),
        (5002, 1002, 4001, '2024-06-28', 650.00),
        (5003, 1003, 4004, '2024-07-19', 2600.00),
        (5004, 1004, 4002, '2024-07-22', 8925.00),
        (5005, 1002, 4002, '2024-07-31', 35500.00),
        (5006, 1003, 4005, '2024-08-15', 1000.00),
        (5007, 1001, 4003, '2024-08-23', 48240.00),
        (5008, 1001, 4002, '2024-09-16', 3410.00),
        (5009, 1004, 4003, '2024-09-26', 1350.00),
        (5010, 1004, 4003, '2024-10-03',1150.00)
    ]
    conn.executemany("""
        INSERT INTO Orders (order_id, customer_id, store_id, order_date, total_amount)
        VALUES (?, ?, ?, ?, ?)""", orders)

    # Insert OrderItems
    items = [
        (5001, 3001, 2, 900.00),
        (5001, 3002, 1, 1785.00),
        (5002, 3003, 1, 650.00),
        (5003, 3003, 4, 2600.00),
        (5004, 3002, 5, 8925.00),
        (5005, 3006, 1, 35500.00),
        (5006, 3007, 2, 1000.00),
        (5007, 3005, 1, 48000.00),
        (5007, 3008, 2, 240.00),
        (5008, 3004, 2, 3200.00),
        (5008, 3009, 3, 210.00),
        (5009, 3001, 3, 1350.00),
        (5010, 3007, 1, 500.00),
        (5010, 3003, 1, 650.00)
    ]
    conn.executemany("""
        INSERT INTO OrderItem (order_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)""", items)

    # Insert Reviews
    reviews = [
        (6001, 1001, 3001, 5, '2025-06-14'),
        (6002, 1001, 3002, 4, '2025-06-16'),
        (6003, 1002, 3003, 3, '2025-07-07'),
        (6004, 1004, 3002, 4, '2025-07-27'),
        (6005, 1003, 3003, 5, '2025-07-31'),
        (6006, 1002, 3006, 3, '2025-08-01'),
        (6007, 1003, 3007, 3, '2025-08-20'),
        (6008, 1001, 3005, 5, '2025-09-01'),
        (6009, 1001, 3008, 3, '2025-09-20'),
        (6010, 1001, 3004, 2, '2025-09-20'),
        (6011, 1001, 3009, 4, '2025-09-20'),
        (6012, 1004, 3001, 3, '2025-10-01'),
        (6013, 1004, 3003, 3, '2025-10-08'),
        (6014, 1004, 3007, 3, '2025-10-08')
    ]
    conn.executemany("""
        INSERT INTO Review (review_id, customer_id, product_id, rating, review_date)
        VALUES (?, ?, ?, ?, ?)""", reviews)


# 2. Sample SELECT queries
print("=== Customers ===")
for row in conn.execute("SELECT * FROM Customer"):
    print(row)

print("\n=== Orders with Customers ===")
q = """
SELECT o.order_id, c.name, o.total_amount
FROM Orders o
JOIN Customer c ON o.customer_id = c.customer_id;
"""
for row in conn.execute(q):
    print(row)

print("\n=== Products and Suppliers ===")
q = """
SELECT p.name, s.name, p.price
FROM Product p
JOIN Supplier s ON p.supplier_id = s.supplier_id;
"""
for row in conn.execute(q):
    print(row)

print("\n=== Reviews ===")
for row in conn.execute("""
SELECT c.name, p.name, r.rating, r.review_date
FROM Review r
JOIN Customer c ON r.customer_id = c.customer_id
JOIN Product p ON r.product_id = p.product_id;
"""):
    print(row)

# Close connection
conn.close()
