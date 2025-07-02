
CREATE TABLE IF NOT EXISTS sales_data (
    timestamp TIMESTAMP,
    customer_id INTEGER,
    category VARCHAR(50),
    purchase_amount NUMERIC(10, 2),
    is_returned BOOLEAN
);