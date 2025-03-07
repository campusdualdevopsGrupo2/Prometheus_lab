FROM python:3.10.12

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY src/ ./src/

# Hacer ejecutable el script principal
RUN chmod +x ./src/main.py

# Exponer el puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["python", "./src/main.py"]