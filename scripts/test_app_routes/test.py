import requests
import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configura las rutas de tu aplicación Flask
BASE_URL = "http://g2-prometheus.campusdual.mkcampus.com/myapp"  # Cambia esto si tu aplicación está en otro host/puerto
ROUTES = [
    ("/", 500),            # Ruta / tiene 50 peticiones a realizar
    ("/api/data", 22500),    # Ruta /api/data tiene 22500 peticiones a realizar
    ("/api/slow", 450),     # Ruta /api/slow tiene 50 peticiones a realizar
    ("/api/error", 2100),   # Ruta /api/error tiene 100 peticiones a realizar
    ("/health", 910)        # Ruta /health tiene 10 peticiones a realizar
]

TOTAL_REQUESTS = 300  # Total de veces que se decidirá qué endpoint probar

def distribute_requests():
    """Distribuye aleatoriamente las peticiones entre las rutas según la cantidad definida en ROUTES"""
    all_requests = []

    # Para cada ruta, repetimos la cantidad de veces que se tiene que hacer la petición
    for route, count in ROUTES:
        all_requests.extend([route] * count)

    # Mezclamos aleatoriamente las rutas para que las peticiones no sean secuenciales
    random.shuffle(all_requests)
    return all_requests

def test_route(route):
    """Función que hace una petición GET a una ruta específica"""
    try:
        response = requests.get(f"{BASE_URL}{route}")
        return (route, response.status_code, response.json())
    except requests.exceptions.RequestException as e:
        return (route, "Error", str(e))

def main():
    """Llama a cada ruta la cantidad especificada de veces"""
    all_requests = distribute_requests()  # Distribuye las peticiones entre las rutas según la configuración

    # Realiza las peticiones de forma paralela
    with ThreadPoolExecutor(max_workers=45) as executor:
        future_to_route = {executor.submit(test_route, route): route for route in all_requests}
        
        # Muestra el progreso de las peticiones
        for future in tqdm(as_completed(future_to_route), total=len(all_requests), desc="Progreso de peticiones"):
            route, status, response = future.result()
            # Aquí puedes imprimir o guardar los resultados si lo deseas
            # print(f"Respuesta de {route}: {status} - {response}")

if __name__ == "__main__":
    main()
