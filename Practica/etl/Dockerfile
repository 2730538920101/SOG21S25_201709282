# Imagen base con Python
FROM python:3.9

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar la API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]