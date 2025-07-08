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
        (5001, 3001, 2, 450.00),
	(5001, 3002, 1, 1785.00),
	(5002, 3003, 1, 650.00),
	(5003, 3003, 4, 650.00),
	(5004, 3002, 5, 1785.00),
	(5005, 3006, 1, 35500.00),
	(5006, 3007, 2, 500.00),
	(5007, 3005, 1, 48000.00),
	(5007, 3008, 2, 120.00),
	(5008, 3004, 2, 1600.00),
	(5008, 3009, 3, 70.00),
	(5009, 3001, 3, 450.00),
	(5010, 3007, 1, 500.00),
	(5010, 3003, 1, 650.00)
    ]
    conn.executemany("""
        INSERT INTO OrderItem (order_id, product_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)""", items)

    # Insert Reviews
    reviews = [
        (6001, 1001, 3001, 5, '2024-06-14'),
	(6002, 1001, 3002, 4, '2024-06-16'),
	(6003, 1002, 3003, 3, '2024-07-07'),
	(6004, 1004, 3002, 4, '2024-07-27'),
	(6005, 1003, 3003, 5, '2024-07-31'),
	(6006, 1002, 3006, 3, '2024-08-15'),
	(6007, 1003, 3007, 3, '2024-08-20'),
	(6008, 1001, 3005, 5, '2024-09-01'),
	(6009, 1001, 3008, 3, '2024-09-20'),
	(6010, 1001, 3004, 2, '2024-09-20'),
	(6011, 1001, 3009, 4, '2024-09-20'),
	(6012, 1004, 3001, 3, '2024-10-01'),
	(6013, 1004, 3003, 3, '2024-10-08'),
	(6014, 1004, 3007, 3, '2024-10-08')
    ]
    conn.executemany("""
        INSERT INTO Review (review_id, customer_id, product_id, rating, review_date)
        VALUES (?, ?, ?, ?, ?)""", reviews)


    # Insert Payment
    payments = [
        (7001, 5001, '2024-06-10', 'Net Banking', 2685.00),
	(7002, 5002, '2024-06-28', 'UPI', 650.00),
	(7003, 5003, '2024-07-19', 'Debit Card', 2600.00),
	(7004, 5004, '2024-07-22', 'Net Banking', 8925.00),
	(7005, 5005, '2024-07-31', 'Credit Card', 35500.00),
	(7006, 5006, '2024-08-15', 'UPI', 1000.00),
	(7007, 5007, '2024-08-23', 'Credit Card', 48240.00),
	(7008, 5008, '2024-09-16', 'UPI', 3410.00),
	(7009, 5009, '2024-10-01', 'Cash', 1350.00),
	(7010, 5010, '2024-10-08', 'Cash', 1150.00)
    ]
    conn.executemany("""
        INSERT INTO Payment (payment_id, order_id, payment_date, payment_method, amount)
	VALUES (?, ?, ?, ?, ?)""", payments)


    # Insert Shipment
    shipments = [
        (8001, 5001, '2024-06-11', '2024-06-14', 'Delivered', 'DHL', 'TRACK101'),
	(8002, 5002, '2024-06-30', '2024-07-06', 'Delivered', 'DHL', 'TRACK102'),
	(8003, 5003, '2024-07-23', '2024-07-26', 'Returned', 'FedEx', 'TRACK103'),
	(8004, 5004, '2024-07-25', '2024-07-27', 'Delivered', 'FedEx', 'TRACK104'),
	(8005, 5005, '2024-08-04', '2024-08-07', 'Delivered', 'DHL', 'TRACK105'),
	(8006, 5006, '2024-08-16', '2024-06-19', 'Delivered', 'FedEx', 'TRACK106'),
	(8007, 5007, '2024-08-25', '2024-08-31', 'Returned', 'FedEx', 'TRACK107'),
	(8008, 5009, '2024-09-17', '2024-06-20', 'Delivered', 'DHL', 'TRACK108'),
	(8009, 5009, '2024-09-27', '2024-10-01', 'Delivered', 'DHL', 'TRACK109'),
	(8010, 5010, '2024-10-05', '2024-10-08', 'Delivered', 'DHL', 'TRACK110')
    ]
    conn.executemany("""
        INSERT INTO Shipment (shipment_id, order_id, shipment_date, delivery_date, delivery_status, courier, tracking_number)
	VALUES (?, ?, ?, ?, ?, ?, ?)""", shipments)

    # Insert Inventory
    inventory = [
        (4001, 3001, 50, '2024-10-30'),
	(4001, 3002, 48, '2024-10-30'),
	(4001, 3003, 55, '2024-10-30'),
	(4001, 3004, 57, '2024-10-30'),
	(4001, 3005, 64, '2024-10-30'),
	(4001, 3006, 78, '2024-10-30'),
	(4001, 3007, 103, '2024-10-30'),
	(4001, 3008, 94, '2024-10-30'),
	(4001, 3009, 88, '2024-10-30'),
	(4002, 3001, 58, '2024-11-02'),
	(4002, 3002, 44, '2024-11-02'),
	(4002, 3003, 50, '2024-11-02'),
	(4002, 3004, 77, '2024-11-02'),
	(4002, 3005, 34, '2024-11-02'),
	(4002, 3006, 83, '2024-11-02'),
	(4002, 3007, 106, '2024-11-02'),
	(4002, 3008, 89, '2024-11-02'),
	(4002, 3009, 111, '2024-11-02'),
	(4003, 3001, 75, '2024-11-04'),
	(4003, 3002, 103, '2024-11-04'),
	(4003, 3003, 84, '2024-11-04'),
	(4003, 3004, 64, '2024-11-04'),
	(4003, 3005, 80, '2024-11-04'),
	(4003, 3006, 96, '2024-11-04'),
	(4003, 3007, 103, '2024-11-04'),
	(4003, 3008, 73, '2024-11-04'),
	(4003, 3009, 39, '2024-11-04'),
	(4004, 3001, 96, '2024-11-06'),
	(4004, 3002, 63, '2024-11-06'),
	(4004, 3003, 54, '2024-11-06'),
	(4004, 3004, 43, '2024-11-06'),
	(4004, 3005, 67, '2024-11-06'),
	(4004, 3006, 77, '2024-11-06'),
	(4004, 3007, 93, '2024-11-06'),
	(4004, 3008, 52, '2024-11-06'),
	(4004, 3009, 50, '2024-11-06'),
	(4005, 3001, 46, '2024-11-08'),
	(4005, 3002, 84, '2024-11-08'),
	(4005, 3003, 74, '2024-11-08'),
	(4005, 3004, 60, '2024-11-08'),
	(4005, 3005, 44, '2024-11-08'),
	(4005, 3006, 39, '2024-11-08'),
	(4005, 3007, 71, '2024-11-08'),
	(4005, 3008, 78, '2024-11-08'),
	(4005, 3009, 90, '2024-11-08')
    ]
    conn.executemany("""
        INSERT INTO Inventory (store_id, product_id, stock_level, last_updated)
	VALUES (?, ?, ?, ?)""", inventory)

    # Insert Promotion
    promotions = [
       (9001, 'Holiday Sale', 10, '2024-11-10', '2024-12-25')
    ]
    conn.executemany("""
        INSERT INTO Promotion (promo_id, name, discount_pct, start_date, end_date)
	VALUES (?, ?, ?, ?, ?)""", promotions)

    
    # Insert ProductPromotion
    productpromotions = [
       (3001, 9001),
       (3002, 9001),
       (3004, 9001),
       (3005, 9001)
    ]
    conn.executemany("""
        INSERT INTO ProductPromotion (product_id, promo_id)
	VALUES (?, ?)""", productpromotions)

    # Insert Loyalty
    loyalty = [
       (1001, 'Platinum', 250, '2024-10-20'),
       (1002, 'Gold', 180, '2024-10-20'),
       (1003, 'Silver', 120, '2024-10-20'),
       (1004, 'Gold', 200, '2024-10-20')
    ]
    conn.executemany("""
        INSERT INTO Loyalty (customer_id, tier, points_balance, last_updated)
	VALUES (?, ?, ?, ?)""", loyalty)

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





