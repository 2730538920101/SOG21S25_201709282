CREATE DATABASE IF NOT EXISTS dwh_ecommerce;
USE dwh_ecommerce;

-- Tabla temporal para cargar los datos
CREATE TABLE temp_orders (
    order_id INT,
    purchase_date VARCHAR(255),
    customer_id INT,
    customer_gender VARCHAR(255),
    customer_age INT,
    product_category VARCHAR(255),
    product_name VARCHAR(255),
    product_price DECIMAL(15,2),
    quantity INT,
    order_total DECIMAL(15,2),
    payment_method VARCHAR(255),
    shipping_region VARCHAR(255)
);

-- Dimensión de clientes
CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY,
    gender ENUM('Masculino', 'Femenino', 'Desconocido') NOT NULL,
    age INT NOT NULL
);

-- Dimensión de productos
CREATE TABLE dim_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL
);

-- Dimensión de fechas
CREATE TABLE dim_dates (
    date_id INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL
);

-- Dimensión de métodos de pago
CREATE TABLE dim_payments (
    payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
    method_name VARCHAR(255) UNIQUE NOT NULL
);

-- Dimensión de regiones de envío
CREATE TABLE dim_shipping_regions (
    shipping_region_id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(255) UNIQUE NOT NULL
);

-- Tabla de hechos (ventas)
CREATE TABLE fact_orders (
    order_id INT PRIMARY KEY,
    date_id INT NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    shipping_region_id INT NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    quantity INT NOT NULL,
    order_total DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (payment_method_id) REFERENCES dim_payments(payment_method_id),
    FOREIGN KEY (shipping_region_id) REFERENCES dim_shipping_regions(shipping_region_id)
);

