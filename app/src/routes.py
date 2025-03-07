"""
Definición de rutas para la aplicación web de ejemplo.
"""
import random
import time
from flask import jsonify, request
from opentelemetry import metrics
from opentelemetry.trace import SpanKind

# Crear medidores personalizados
meter = metrics.get_meter("example-app")
request_counter = meter.create_counter(
    name="http.requests",
    description="Número de peticiones HTTP",
    unit="1",
)
request_duration = meter.create_histogram(
    name="http.request.duration",
    description="Duración de las peticiones HTTP",
    unit="ms",
)

def register_routes(app, tracer):
    """
    Registra las rutas de la aplicación.
    
    Args:
        app: La aplicación Flask
        tracer: El trazador de OpenTelemetry
    """
    
    @app.route('/')
    def home():
        with tracer.start_as_current_span("home_route", kind=SpanKind.SERVER):
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "home", "method": "GET"})
            
            # Simular carga de trabajo
            time.sleep(random.uniform(0.05, 0.2))
            
            # Registrar duración
            request_duration.record(
                time.time() - request.start_time,
                {"endpoint": "home", "method": "GET"}
            )
            
            return jsonify({
                "message": "¡Bienvenido a la aplicación de ejemplo!",
                "status": "OK"
            })
    
    @app.route('/api/data')
    def get_data():
        with tracer.start_as_current_span("get_data_route", kind=SpanKind.SERVER):
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "api/data", "method": "GET"})
            
            # Simular carga de trabajo
            time.sleep(random.uniform(0.1, 0.3))
            
            # Registrar duración
            request_duration.record(
                time.time() - request.start_time,
                {"endpoint": "api/data", "method": "GET"}
            )
            
            # Generar datos aleatorios
            data = [
                {"id": i, "value": random.randint(1, 100)}
                for i in range(1, 11)
            ]
            
            return jsonify({"data": data})
    
    @app.route('/api/slow')
    def slow_endpoint():
        with tracer.start_as_current_span("slow_endpoint_route", kind=SpanKind.SERVER):
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "api/slow", "method": "GET"})
            
            # Simular un endpoint lento
            time.sleep(random.uniform(1.0, 3.0))
            
            # Registrar duración
            request_duration.record(
                time.time() - request.start_time,
                {"endpoint": "api/slow", "method": "GET"}
            )
            
            return jsonify({"message": "Esta es una respuesta lenta"})
    
    @app.route('/api/error')
    def error_endpoint():
        with tracer.start_as_current_span("error_endpoint_route", kind=SpanKind.SERVER):
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "api/error", "method": "GET"})
            
            # Simular un error aleatorio
            if random.random() < 0.7:  # 70% de probabilidad de error
                # Registrar duración antes de generar el error
                request_duration.record(
                    time.time() - request.start_time,
                    {"endpoint": "api/error", "method": "GET", "status": "error"}
                )
                
                # Generar una excepción
                raise Exception("Error simulado en el endpoint")
            
            # Registrar duración para solicitudes exitosas
            request_duration.record(
                time.time() - request.start_time,
                {"endpoint": "api/error", "method": "GET", "status": "success"}
            )
            
            return jsonify({"message": "Esta vez no hubo error"})
    
    @app.route('/health')
    def health_check():
        with tracer.start_as_current_span("health_check_route", kind=SpanKind.SERVER):
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "health", "method": "GET"})
            
            # Registrar duración
            request_duration.record(
                time.time() - request.start_time,
                {"endpoint": "health", "method": "GET"}
            )
            
            return jsonify({
                "status": "UP",
                "version": "1.0.0",
                "timestamp": time.time()
            })