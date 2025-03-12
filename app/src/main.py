#!/usr/bin/env python3
"""
Aplicación web de ejemplo instrumentada con OpenTelemetry y Prometheus.
"""
import logging
import random
import time
from flask import Flask, jsonify, request
from telemetry import setup_telemetry
from routes import register_routes
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Inicializar OpenTelemetry con soporte para métricas
# Ahora setup_telemetry() configura Prometheus y devuelve tracer y meter
tracer, meter = setup_telemetry("example-app")

# Instrumentar automáticamente Flask con OpenTelemetry
FlaskInstrumentor().instrument_app(app)

# Crear contadores para los errores
error_counter = meter.create_counter(
    name="app_errors_total",
    description="Número total de errores por tipo",
    unit="1"
)
'''
# Agregar ruta para la URL raíz
@app.route('/')
def home():
    return jsonify({"message": "¡Bienvenido a la aplicación web de ejemplo!"})
'''
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
    
    # Si es un error, incrementar contador de errores por código
    if response.status_code >= 400:
        error_counter.add(
            1, 
            {"error_type": "http", "status_code": str(response.status_code)}
        )
    
    # Agregamos un pequeño retardo aleatorio para simular latencia variable
    time.sleep(random.uniform(0.01, 0.1))
    
    return response

# Middleware para capturar excepciones
@app.errorhandler(Exception)
def handle_exception(e):
    # Registrar el error en el log
    logger.error(f"Error no manejado: {str(e)}", exc_info=True)
    
    # Incrementar contador de errores por tipo de excepción
    error_counter.add(
        1, 
        {"error_type": "exception", "exception_class": e.__class__.__name__}
    )
    
    return jsonify({"error": "Internal Server Error"}), 500

# Punto de entrada principal
if __name__ == "__main__":
    logger.info("Iniciando aplicación web de ejemplo...")
    logger.info("Servidor de métricas Prometheus iniciado en puerto 9464 (/metrics)")
    app.run(host='0.0.0.0', port=8000)
