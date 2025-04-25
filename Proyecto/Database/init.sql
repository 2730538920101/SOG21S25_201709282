-- Crear base de datos
CREATE DATABASE IF NOT EXISTS empresa_ventas;
USE empresa_ventas;

-- Crear tabla clientes
CREATE TABLE IF NOT EXISTS clientes (
    id VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    gender VARCHAR(255),
    phone VARCHAR(255),
    cliente VARCHAR(255)
);

-- Crear tabla proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    gender VARCHAR(255),
    phone VARCHAR(255),
    cliente VARCHAR(255)
);
