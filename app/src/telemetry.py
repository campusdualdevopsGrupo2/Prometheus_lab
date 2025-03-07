"""
Configuración de OpenTelemetry para la aplicación web de ejemplo.
"""
import os
from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Se agregó la instancia de Flask
app = Flask(__name__)

def setup_telemetry(service_name):
    """
    Configura OpenTelemetry para trazas y métricas.
    
    Args:
        service_name: Nombre del servicio
        
    Returns:
        tracer: El trazador configurado
    """
    # Obtener el endpoint del exportador OTLP desde las variables de entorno
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    
    # Configurar recursos para identificar el servicio
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": "development"
    })
    
    # Configurar el proveedor de trazas
    tracer_provider = TracerProvider(resource=resource)
    
    # Crear un exportador OTLP para trazas
    otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    
    # Agregar el procesador de spans al proveedor de trazas
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
    
    # Establecer el proveedor de trazas global
    trace.set_tracer_provider(tracer_provider)
    
    # Crear un trazador para el servicio
    tracer = trace.get_tracer(service_name)
    
    # Configurar el proveedor de métricas
    otlp_metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
    reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    
    # Establecer el proveedor de métricas global
    metrics.set_meter_provider(meter_provider)
    
    # Instrumentar automáticamente las librerías comunes
    RequestsInstrumentor().instrument()
    
    # Se modificó para pasar la instancia `app` correctamente
    FlaskInstrumentor().instrument_app(
        app,  # Se pasa la instancia de Flask aquí
        enable_commenter=True,
        excluded_urls="^/static/.*",
        tracer_provider=tracer_provider,
    )
    
    return tracer