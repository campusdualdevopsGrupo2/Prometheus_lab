import random
import time
import logging
from flask import Flask, jsonify, request
from opentelemetry import metrics
from opentelemetry.trace import TracerProvider, SpanKind
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import Counter, Histogram

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myapp")

# Definir prefijo para las rutas
route_prefix = "/myapp"

def register_routes(app, tracer):
    """
    Registra las rutas de la aplicación.
    
    Args:
        app: La aplicación Flask
        tracer: El trazador de OpenTelemetry
    """
    # Crear medidores personalizados
    meter = metrics.get_meter("example-app")
    request_counter = meter.create_counter(
        name="http_requests",
        description="Número de peticiones HTTP",
        unit="1",
    )
    #request_duration = meter.create_histogram(
    #    name="http_request_duration",
    #    description="Duración de las peticiones HTTP",
    #    unit="ms",
    #)
    
    @app.route(route_prefix+'/')
    def home():
        with tracer.start_as_current_span("home_route", kind=SpanKind.SERVER) as span:
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "home", "method": "GET"})
            
            # Simular carga de trabajo
            time.sleep(random.uniform(0.05, 0.2))
            
            # Registrar duración (automática con el span)
            span.set_attribute("endpoint", "home")
            span.set_attribute("method", "GET")
            span.set_attribute("status", "success")
            
            return jsonify({
                "message": "¡Bienvenido a la aplicación de ejemplo!",
                "status": "OK"
            })
    
    @app.route(route_prefix+'/api/data')
    def get_data():
        with tracer.start_as_current_span("get_data_route", kind=SpanKind.SERVER) as span:
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "api/data", "method": "GET"})
            
            # Simular carga de trabajo
            time.sleep(random.uniform(0.1, 0.3))
            
            # Registrar duración (automática con el span)
            span.set_attribute("endpoint", "api/data")
            span.set_attribute("method", "GET")
            span.set_attribute("status", "success")
            
            # Generar datos aleatorios
            data = [
                {"id": i, "value": random.randint(1, 100)}
                for i in range(1, 11)
            ]
            
            return jsonify({"data": data})
    
    @app.route(route_prefix+'/api/slow')
    def slow_endpoint():
        with tracer.start_as_current_span("slow_endpoint_route", kind=SpanKind.SERVER) as span:
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "api/slow", "method": "GET"})
            
            # Simular un endpoint lento
            time.sleep(random.uniform(1.0, 3.0))
            
            # Registrar duración (automática con el span)
            span.set_attribute("endpoint", "api/slow")
            span.set_attribute("method", "GET")
            span.set_attribute("status", "success")
            
            return jsonify({"message": "Esta es una respuesta lenta"})
    
    @app.route(route_prefix+'/api/error')
    def error_endpoint():
        with tracer.start_as_current_span("error_endpoint_route", kind=SpanKind.SERVER) as span:
            # Incrementar contador de solicitudes
            request_counter.add(1, {"endpoint": "api/error", "method": "GET"})
            
            try:
                # Simular un error aleatorio
                if random.random() < 0.7:  # 70% de probabilidad de error
                    span.set_attribute("status", "error")
                    raise Exception("Error simulado en el endpoint")
                
                span.set_attribute("status", "success")
                return jsonify({"message": "Esta vez no hubo error"})
            
            except Exception as e:
                # Registrar la excepción en el span
                span.set_attribute("error", str(e))
                raise e
    
    @app.route(route_prefix+'/health')
    def health_check():
        with tracer.start_as_current_span("health_check_route", kind=SpanKind.SERVER) as span:
            # Incrementar contador de solicitudes
            logger.info(f"Received request to {route_prefix}/health (Health Check) - Method: {request.method}")
            request_counter.add(1, {"endpoint": "health", "method": "GET"})
            
            # Registrar duración (automática con el span)
            span.set_attribute("endpoint", "health")
            span.set_attribute("method", "GET")
            span.set_attribute("status", "success")
            
            return jsonify({
                "status": "UP",
                "version": "1.0.0",
                "timestamp": time.time()
            })
