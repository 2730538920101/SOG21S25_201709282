import os
from fastapi import FastAPI
from connection import create_connection, close_connection
from funciones import (
    load_csv, insert_into_temp_table, clean_and_transform_data,
    insert_into_dim_customers, insert_into_dim_products, insert_into_dim_dates,
    insert_into_dim_payments, insert_into_dim_shipping_regions, insert_into_fact_orders
)

app = FastAPI()

@app.get("/call_etl")
def ejecutar_etl():
    file_path = os.getenv('CSV_FILE_PATH', 'ventas_tienda_online.csv')
    df = load_csv(file_path)

    if df is None:
        return {"message": "Error al cargar el archivo CSV"}

    connection = create_connection()
    if not connection:
        return {"message": "Error en la conexión con la base de datos"}

    # Procesar ETL
    insert_into_temp_table(df, connection)
    df_cleaned = clean_and_transform_data(connection)

    insert_into_dim_customers(df_cleaned, connection)
    insert_into_dim_products(df_cleaned, connection)
    insert_into_dim_dates(df_cleaned, connection)
    insert_into_dim_payments(df_cleaned, connection)
    insert_into_dim_shipping_regions(df_cleaned, connection)
    insert_into_fact_orders(df_cleaned, connection)

    close_connection(connection)
    return {"message": "ETL ejecutada correctamente"}