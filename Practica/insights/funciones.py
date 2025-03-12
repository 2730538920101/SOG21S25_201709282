import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from connection import create_connection, close_connection  # Importar funciones de connection.py

# Función para obtener los datos de la base de datos
def get_data():
    connection = create_connection()
    
    # Consulta SQL para obtener los datos necesarios de las tablas
    query = """
        SELECT f.order_id, f.order_total, f.quantity, f.price, f.date_id, f.customer_id, f.product_id, 
               f.payment_method_id, f.shipping_region_id, f.date_id, c.gender, c.age, p.category, p.product_name, 
               s.region_name, d.full_date
        FROM fact_orders f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        JOIN dim_products p ON f.product_id = p.product_id
        JOIN dim_shipping_regions s ON f.shipping_region_id = s.shipping_region_id
        JOIN dim_dates d ON f.date_id = d.date_id
    """
    
    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(query)
    
    # Obtener los resultados
    results = cursor.fetchall()
    
    # Convertir los resultados en un DataFrame de pandas
    columns = ['order_id', 'order_total', 'quantity', 'price', 'date_id', 'customer_id', 'product_id', 
               'payment_method_id', 'shipping_region_id', 'date_id', 'gender', 'age', 'category', 
               'product_name', 'region_name', 'full_date']
    data = pd.DataFrame(results, columns=columns)
    
    # Cerrar la conexión
    cursor.close()
    close_connection(connection)
    
    return data

# Análisis exploratorio
def exploratory_analysis(data):
    # Calcular estadísticas básicas
    numerical_data = data[['order_total', 'quantity', 'price', 'age']]
    
    mean = numerical_data.mean()
    median = numerical_data.median()
    mode = numerical_data.mode().iloc[0]

    print("Media:\n", mean)
    print("\nMediana:\n", median)
    print("\nModa:\n", mode)
    
    # Distribución de ventas por categoría de producto
    plt.figure(figsize=(10, 6))
    sns.barplot(x='category', y='order_total', data=data, estimator=sum)
    plt.title('Distribución de ventas por categoría de producto')
    plt.xticks(rotation=45)
    plt.show()

    # Distribución de ventas por región de envío
    plt.figure(figsize=(10, 6))
    sns.barplot(x='region_name', y='order_total', data=data, estimator=sum)
    plt.title('Distribución de ventas por región de envío')
    plt.xticks(rotation=45)
    plt.show()

# Análisis de tendencias
def trend_analysis(data):
    # Convertir la columna de fecha a tipo datetime
    data['full_date'] = pd.to_datetime(data['full_date'])

    # Agregar por mes
    monthly_sales = data.groupby(data['full_date'].dt.to_period('M')).agg({'order_total': 'sum'}).reset_index()

    # Identificar los meses con mayores y menores ventas
    max_sales_month = monthly_sales.loc[monthly_sales['order_total'].idxmax()]
    min_sales_month = monthly_sales.loc[monthly_sales['order_total'].idxmin()]

    print(f"Mes con mayores ventas: {max_sales_month['full_date']}, Ventas: {max_sales_month['order_total']}")
    print(f"Mes con menores ventas: {min_sales_month['full_date']}, Ventas: {min_sales_month['order_total']}")

    # Ventas totales por producto
    product_sales = data.groupby('product_name').agg({'order_total': 'sum'}).reset_index()

    # Ordenar por ventas
    product_sales = product_sales.sort_values('order_total', ascending=False)

    # Mostrar los más vendidos
    print("Productos más vendidos:\n", product_sales.head(10))

    # Mostrar los menos vendidos
    print("Productos menos vendidos:\n", product_sales.tail(10))

# Segmentación de clientes
def customer_segmentation(data):
    # Agrupar por edad
    age_groups = data.groupby('age').agg({'order_total': 'sum', 'quantity': 'sum'}).reset_index()

    # Visualizar patrones de compra por edad
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='age', y='order_total', data=age_groups)
    plt.title('Patrones de compra por edad')
    plt.show()

    # Comparar por género
    gender_sales = data.groupby('gender').agg({'order_total': 'sum'}).reset_index()

    # Visualizar comparación de compras por género
    plt.figure(figsize=(10, 6))
    sns.barplot(x='gender', y='order_total', data=gender_sales)
    plt.title('Comparación de compras entre géneros')
    plt.show()

# Análisis de correlación
def correlation_analysis(data):
    # Correlación entre total de la orden y edad del cliente
    correlation = data[['order_total', 'age']].corr()
    print("Correlación entre total de la orden y edad del cliente:")
    print(correlation)

    # Visualizar la correlación
    sns.heatmap(correlation, annot=True, cmap='coolwarm')
    plt.title('Correlación entre total de la orden y edad del cliente')
    plt.show()

    # Correlación entre la categoría del producto y el método de pago
    category_payment_corr = pd.crosstab(data['category'], data['payment_method_id'])
    sns.heatmap(category_payment_corr, annot=True, cmap='Blues')
    plt.title('Correlación entre categoría de producto y método de pago')
    plt.show()