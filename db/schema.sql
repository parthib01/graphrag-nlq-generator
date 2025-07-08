-- ===========================
-- Retail Database: Complex Schema
-- ===========================

-- Customer table
CREATE TABLE Customer (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    phone_number  TEXT    NOT NULL
);

-- Supplier table
CREATE TABLE Supplier (
    supplier_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    region        TEXT
);

-- Product table
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

-- Store table
CREATE TABLE Store (
    store_id   INTEGER PRIMARY KEY,
    location   TEXT,
    region     TEXT,
    type       TEXT
);

-- Orders table
CREATE TABLE Orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL,
    store_id      INTEGER,
    order_date    TEXT    NOT NULL,
    total_amount  REAL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (store_id)    REFERENCES Store(store_id)
);

-- OrderItem table
CREATE TABLE OrderItem (
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL    NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id)   REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- Review table
CREATE TABLE Review (
    review_id    INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_date  TEXT    NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (product_id)  REFERENCES Product(product_id)
);

-- Payment table
CREATE TABLE Payment (
    payment_id     INTEGER PRIMARY KEY,
    order_id       INTEGER NOT NULL,
    payment_date   TEXT NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash')),
    amount         REAL NOT NULL CHECK (amount >= 0),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

-- Shipment table
CREATE TABLE Shipment (
    shipment_id     INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    shipment_date   TEXT NOT NULL,
    delivery_date   TEXT,
    delivery_status TEXT CHECK(delivery_status IN ('Pending', 'Shipped', 'Delivered', 'Returned')),
    courier         TEXT,
    tracking_number TEXT UNIQUE,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

-- Inventory table
CREATE TABLE Inventory (
    store_id     INTEGER NOT NULL,
    product_id   INTEGER NOT NULL,
    stock_level  INTEGER NOT NULL CHECK (stock_level >= 0),
    last_updated TEXT,
    PRIMARY KEY (store_id, product_id),
    FOREIGN KEY (store_id) REFERENCES Store(store_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- Promotion table
CREATE TABLE Promotion (
    promo_id     INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    discount_pct REAL CHECK (discount_pct BETWEEN 0 AND 100),
    start_date   TEXT NOT NULL,
    end_date     TEXT NOT NULL
);

-- ProductPromotion table
CREATE TABLE ProductPromotion (
    product_id INTEGER NOT NULL,
    promo_id   INTEGER NOT NULL,
    PRIMARY KEY (product_id, promo_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id),
    FOREIGN KEY (promo_id)   REFERENCES Promotion(promo_id)
);

-- Loyalty table
CREATE TABLE Loyalty (
    customer_id    INTEGER PRIMARY KEY,
    tier           TEXT CHECK(tier IN ('Silver', 'Gold', 'Platinum')),
    points_balance INTEGER DEFAULT 0,
    last_updated   TEXT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);