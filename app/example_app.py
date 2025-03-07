from flask import Flask
from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import make_wsgi_app


import random
import time

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de OpenTelemetry para trazas
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "flask-otel-service"})
    )
)
tracer = trace.get_tracer(__name__)

# Configuración de OpenTelemetry para métricas
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)

# Exportador de métricas Prometheus
exporter = PrometheusMetricsExporter()
metric_reader = PeriodicExportingMetricReader(exporter, 5)  # Exporta cada 5 segundos
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Instrumentación de Flask con OpenTelemetry
FlaskInstrumentor().instrument_app(app)

# Crear una métrica simple
requests_counter = meter.create_counter(
    "flask_requests_total", description="Total Flask requests"
)

@app.route('/')
def hello():
    with tracer.start_as_current_span("hello-span"):
        # Simulamos una latencia aleatoria
        time.sleep(random.uniform(0.1, 0.5))
        
        # Incrementar el contador de solicitudes
        requests_counter.add(1, {"status": "success"})
        
        return "Hello, OpenTelemetry with Flask!"

# Endpoint de métricas para Prometheus
@app.route('/metrics')
def metrics_endpoint():
    return make_wsgi_app()

# Iniciar el servidor Prometheus
#tart_http_server(8000)

if __name__ == '__main__':
    # Iniciar la aplicación Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
