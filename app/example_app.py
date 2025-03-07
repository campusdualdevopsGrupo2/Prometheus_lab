from flask import Flask, request
from random import randint
import logging

# OpenTelemetry Imports
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.exporter.prometheus import PrometheusExporter
from prometheus_client import start_http_server

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de OpenTelemetry - Trace
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "dice-server"})
    )
)

# Configuración del Tracer
tracer = trace.get_tracer("diceroller.tracer")

# Configuración de OpenTelemetry - Metrics
metrics.set_meter_provider(
    MeterProvider(
        resource=Resource.create({SERVICE_NAME: "dice-server"})
    )
)
meter = metrics.get_meter("diceroller.meter")
roll_counter = meter.create_counter(
    "dice.rolls",
    description="Cuenta el número de tiradas por valor",
)

# Crear la aplicación Flask usando el patrón de fábrica
def create_app():
    app = Flask(__name__)

    # Instrumentar Flask automáticamente
    FlaskInstrumentor().instrument_app(app)

    # Inicia el servidor de métricas Prometheus en el puerto 8000
    start_http_server(8000)

    # Configura el exportador de métricas para Prometheus
    prometheus_exporter = PrometheusExporter()
    metrics.get_meter_provider().add_exporter(prometheus_exporter)

    # Definir rutas
    @app.route("/rolldice")
    def roll_dice():
        # Esta sección crea un span hijo de la solicitud actual
        with tracer.start_as_current_span("roll") as roll_span:
            player = request.args.get('player', default=None, type=str)
            result = str(roll())

            # Configura atributos de la traza
            roll_span.set_attribute("roll.value", result)
            
            # Añadir métrica de conteo de tiradas
            roll_counter.add(1, {"roll.value": result})

            # Loguea la tirada
            if player:
                logger.warning(f"{player} está lanzando los dados: {result}")
            else:
                logger.warning(f"Jugador anónimo está lanzando los dados: {result}")
            
            return result

    return app

# Función de tirada de dados
def roll():
    return randint(1, 6)

# Iniciar la aplicación Flask
if __name__ == "__main__":
    app = create_app()
    app.run(port=8080)
