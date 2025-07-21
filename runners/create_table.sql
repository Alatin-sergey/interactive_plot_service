CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    customer_id INTEGER,
    category VARCHAR(50),
    purchase_amount NUMERIC(10, 2),
    is_returned BOOLEAN
);