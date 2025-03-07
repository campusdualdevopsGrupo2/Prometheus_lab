#!/usr/bin/env python3
"""
Aplicación web de ejemplo instrumentada con OpenTelemetry.
"""
import logging
import random
import time
from flask import Flask, jsonify, request
from telemetry import setup_telemetry
from routes import register_routes

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Inicializar OpenTelemetry
tracer = setup_telemetry("example-app")

# Registrar rutas
register_routes(app, tracer)

# Middleware para medir el tiempo de respuesta
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Calcular el tiempo de respuesta
    request_time = time.time() - request.start_time
    
    # Agregar cabeceras de tiempo de respuesta
    response.headers["X-Response-Time"] = str(request_time)
    
    # Loguear información de la solicitud
    logger.info(
        f"Request: {request.method} {request.path} - "
        f"Status: {response.status_code} - "
        f"Time: {request_time:.4f}s"
    )
    
    # Agregamos un pequeño retardo aleatorio para simular latencia variable
    time.sleep(random.uniform(0.01, 0.1))
    
    return response

# Middleware para capturar excepciones
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Error no manejado: {str(e)}", exc_info=True)
    return jsonify({"error": "Internal Server Error"}), 500

# Punto de entrada principal
if __name__ == "__main__":
    logger.info("Iniciando aplicación web de ejemplo...")
    app.run(host='0.0.0.0', port=8000)