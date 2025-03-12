import pandas as pd

# Función para cargar el CSV (sin limpiar los datos aún)
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None

def insert_into_temp_table(df, connection):
    cursor = connection.cursor()
    try:
        for _, row in df.iterrows():
            if row[['order_id', 'purchase_date', 'customer_id', 'product_category']].isnull().any():
                print(f"Fila omitida por NaN: {row}")
                continue
            if any(row[col] == '' for col in ['order_id', 'purchase_date', 'customer_id', 'product_category']):
                print(f"Fila omitida por vacío: {row}")
                continue

            query = """
            INSERT INTO temp_orders (order_id, purchase_date, customer_id, customer_gender, customer_age, 
                                    product_category, product_name, product_price, quantity, order_total, 
                                    payment_method, shipping_region)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convert NaN values to None for SQL NULL
            values = [None if pd.isna(row[col]) else row[col] for col in ['order_id', 'purchase_date', 'customer_id', 'customer_gender',
                                                'customer_age', 'product_category', 'product_name', 'product_price',
                                                'quantity', 'order_total', 'payment_method', 'shipping_region']]
            
            try:
                cursor.execute(query, values)
            except Exception as e:
                print(f"Error al insertar fila: {row} - {e}")
                continue
        connection.commit()
        print("Datos insertados en la tabla temporal exitosamente")
    except Exception as e:
        print(f"Error en la inserción: {e}")
        connection.rollback()
    finally:
        cursor.close()

def clean_and_transform_data(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM temp_orders")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=['order_id', 'purchase_date', 'customer_id', 'customer_gender', 'customer_age',
                                         'product_category', 'product_name', 'product_price', 'quantity',
                                         'order_total', 'payment_method', 'shipping_region'])

        df['purchase_date'] = pd.to_datetime(df['purchase_date'], format='%d/%m/%y', errors='coerce')

        # Convertir valores numéricos, forzando errores a NaN y eliminando valores inválidos
        df[['product_price', 'order_total', 'quantity']] = df[['product_price', 'order_total', 'quantity']].apply(pd.to_numeric, errors='coerce')
        df.dropna(subset=['product_price', 'order_total', 'quantity'], inplace=True)

        # Rellenar valores nulos con valores predeterminados
        df.fillna({'customer_gender': 'Desconocido', 'customer_age': 0, 'product_name': 'Desconocido',
                   'shipping_region': 'Desconocido'}, inplace=True)

        return df
    finally:
        cursor.close()


# Función para insertar los datos transformados en la tabla dim_customers
def insert_into_dim_customers(df, connection):
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO dim_customers (customer_id, gender, age)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE gender = VALUES(gender), age = VALUES(age)
        """
        # Filtrar filas con valores NaN antes de la inserción
        df_clean = df.dropna(subset=['customer_id', 'customer_gender', 'customer_age'])
        values = df_clean[['customer_id', 'customer_gender', 'customer_age']].values.tolist()

        cursor.executemany(query, values)
        connection.commit()
        print("Datos insertados en dim_customers exitosamente")
    except Exception as e:
        print(f"Error al insertar datos en dim_customers: {e}")
        connection.rollback()

# Función para insertar los datos transformados en la tabla dim_products
def insert_into_dim_products(df, connection):
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO dim_products (category, product_name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE category = VALUES(category), product_name = VALUES(product_name)
        """
        # Filtrar filas con product_name diferente de "Desconocido" y sin valores NaN
        filtered_df = df[(df['product_name'] != 'Desconocido') & df[['product_category', 'product_name']].notna().all(axis=1)]
        unique_products = set(tuple(x) for x in filtered_df[['product_category', 'product_name']].values.tolist())
        
        if unique_products:  # Verificar que haya productos para insertar
            cursor.executemany(query, list(unique_products))
            connection.commit()
            print("Datos insertados en dim_products exitosamente")
        else:
            print("No hay productos válidos para insertar en dim_products")
            
    except Exception as e:
        print(f"Error al insertar datos en dim_products: {e}")
        connection.rollback()
    finally:
        cursor.close()

# Función para insertar los datos transformados en la tabla dim_dates
def insert_into_dim_dates(df, connection):
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO dim_dates (full_date, year, quarter, month, day, day_of_week)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE year = VALUES(year), quarter = VALUES(quarter), month = VALUES(month), 
                                day = VALUES(day), day_of_week = VALUES(day_of_week)
        """

        # Eliminar valores NaT antes de procesar
        df_clean = df.dropna(subset=['purchase_date']).copy()

        # Convertir fechas a datetime si no lo son
        df_clean['purchase_date'] = pd.to_datetime(df_clean['purchase_date'], format='%d/%m/%y', errors='coerce')

        values = [
            (
                date.date(),  # full_date
                date.year,
                (date.month - 1) // 3 + 1,  # quarter
                date.month,
                date.day,
                date.strftime('%A')  # Nombre del día de la semana
            )
            for date in df_clean['purchase_date'] if not pd.isna(date)
        ]

        cursor.executemany(query, values)
        connection.commit()
        print("Datos insertados en dim_dates exitosamente")
    except Exception as e:
        print(f"Error al insertar datos en dim_dates: {e}")
        connection.rollback()
    finally:
        cursor.close()

# Función para insertar los datos transformados en la tabla dim_payments
def insert_into_dim_payments(df, connection):
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO dim_payments (method_name)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE method_name = VALUES(method_name)
        """
        # Filtrar filas con valores NaN antes de la inserción
        df_clean = df.dropna(subset=['payment_method'])
        values = df_clean[['payment_method']].values.tolist()

        cursor.executemany(query, values)
        connection.commit()
        print("Datos insertados en dim_payments exitosamente")
    except Exception as e:
        print(f"Error al insertar datos en dim_payments: {e}")
        connection.rollback()

# Función para insertar los datos transformados en la tabla dim_shipping_regions
def insert_into_dim_shipping_regions(df, connection):
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO dim_shipping_regions (region_name)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE region_name = VALUES(region_name)
        """
        # Filtrar filas con valores NaN antes de la inserción
        df_clean = df.dropna(subset=['shipping_region'])
        values = df_clean[['shipping_region']].values.tolist()

        cursor.executemany(query, values)
        connection.commit()
        print("Datos insertados en dim_shipping_regions exitosamente")
    except Exception as e:
        print(f"Error al insertar datos en dim_shipping_regions: {e}")
        connection.rollback()

# Función para insertar los datos transformados en la tabla fact_orders
def insert_into_fact_orders(df, connection):
    cursor = connection.cursor()
    
    try:
        # Primero, necesitamos obtener los IDs de las tablas dimensionales
        
        # Obtener id de fecha
        cursor.execute("SELECT date_id, full_date FROM dim_dates")
        date_mapping = {row[1].strftime('%Y-%m-%d'): row[0] for row in cursor.fetchall()}
        
        # Obtener id de producto
        cursor.execute("SELECT product_id, category, product_name FROM dim_products")
        product_mapping = {(row[1], row[2]): row[0] for row in cursor.fetchall()}
        
        # Obtener id de método de pago
        cursor.execute("SELECT payment_method_id, method_name FROM dim_payments")
        payment_mapping = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Obtener id de región de envío
        cursor.execute("SELECT shipping_region_id, region_name FROM dim_shipping_regions")
        region_mapping = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Preparar los datos para inserción en fact_orders
        values = []
        skipped_rows = 0
        
        for _, row in df.iterrows():
            # Convertir la fecha al formato correcto para buscar en el mapping
            date_str = row['purchase_date'].strftime('%Y-%m-%d') if pd.notnull(row['purchase_date']) else None
            
            # Verificar que todos los valores necesarios existan
            if (date_str is None or 
                date_str not in date_mapping or
                (row['product_category'], row['product_name']) not in product_mapping or
                row['payment_method'] not in payment_mapping or
                row['shipping_region'] not in region_mapping):
                skipped_rows += 1
                continue
            
            # Obtener los IDs de las dimensiones
            date_id = date_mapping[date_str]
            product_id = product_mapping[(row['product_category'], row['product_name'])]
            payment_method_id = payment_mapping[row['payment_method']]
            shipping_region_id = region_mapping[row['shipping_region']]
            
            # Agregar a la lista de valores para inserción
            values.append((
                int(row['order_id']),  # order_id
                date_id,                # date_id
                int(row['customer_id']), # customer_id
                product_id,             # product_id
                payment_method_id,      # payment_method_id
                shipping_region_id,     # shipping_region_id
                float(row['product_price']), # price
                int(row['quantity']),   # quantity
                float(row['order_total']) # order_total
            ))
        
        # Insertar en fact_orders
        if values:
            query = """
            INSERT INTO fact_orders (order_id, date_id, customer_id, product_id, 
                                     payment_method_id, shipping_region_id, 
                                     price, quantity, order_total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                date_id = VALUES(date_id),
                customer_id = VALUES(customer_id),
                product_id = VALUES(product_id),
                payment_method_id = VALUES(payment_method_id),
                shipping_region_id = VALUES(shipping_region_id),
                price = VALUES(price),
                quantity = VALUES(quantity),
                order_total = VALUES(order_total)
            """
            
            cursor.executemany(query, values)
            connection.commit()
            print(f"Datos insertados en fact_orders exitosamente. {len(values)} registros insertados, {skipped_rows} omitidos.")
        else:
            print("No hay datos válidos para insertar en fact_orders.")
            
    except Exception as e:
        print(f"Error al insertar datos en fact_orders: {e}")
        connection.rollback()
    finally:
        cursor.close()