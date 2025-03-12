# Usar una imagen base con Jupyter preinstalado
FROM jupyter/base-notebook

# Establecer el directorio de trabajo
WORKDIR /home/jovyan/work

# Copiar archivos del proyecto al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Jupyter
EXPOSE 8888

# Comando para ejecutar Jupyter Notebook al iniciar el contenedor
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]