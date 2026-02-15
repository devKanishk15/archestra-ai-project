-- PostgreSQL Initialization Script
-- Creates the products table for storing transformed data from Elasticsearch

-- Create extension for better data types if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    description TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ratings DECIMAL(3, 2) CHECK (ratings >= 0 AND ratings <= 5),
    reviews_count INTEGER DEFAULT 0 CHECK (reviews_count >= 0),
    brand VARCHAR(100),
    tags TEXT[], -- PostgreSQL array for tags
    imported_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products(subcategory);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_ratings ON products(ratings);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);
CREATE INDEX IF NOT EXISTS idx_products_tags ON products USING GIN(tags);

-- Create a view for product statistics
CREATE OR REPLACE VIEW product_stats AS
SELECT 
    category,
    subcategory,
    COUNT(*) as product_count,
    AVG(price) as avg_price,
    SUM(stock_quantity) as total_stock,
    AVG(ratings) as avg_rating
FROM products
GROUP BY category, subcategory
ORDER BY category, subcategory;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_products_modtime
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Grant necessary permissions (adjust as needed)
GRANT ALL PRIVILEGES ON TABLE products TO admin;
GRANT SELECT ON product_stats TO admin;

-- Insert a sample record to verify table creation
INSERT INTO products (
    id, name, category, subcategory, price, description, 
    stock_quantity, created_at, ratings, reviews_count, brand, tags
) VALUES (
    'SAMPLE-000',
    'Sample Product',
    'Sample Category',
    'Sample Subcategory',
    0.01,
    'This is a sample product to verify table creation',
    0,
    CURRENT_TIMESTAMP,
    0.0,
    0,
    'Sample Brand',
    ARRAY['sample', 'test']
) ON CONFLICT (id) DO NOTHING;

-- Display table info
SELECT 
    'Products table created successfully' as status,
    COUNT(*) as initial_records
FROM products;
