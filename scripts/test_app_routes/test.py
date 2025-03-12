import requests
import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configura las rutas de tu aplicación Flask
BASE_URL = "http://g2-prometheus.campusdual.mkcampus.com/myapp"  # Cambia esto si tu aplicación está en otro host/puerto
ROUTES = [
    ("/", 0),            # Ruta / inicialmente con 0 peticiones
    ("/api/data", 0),     # Ruta /api/data inicialmente con 0 peticiones
    ("/api/slow", 0),     # Ruta /api/slow inicialmente con 0 peticiones
    ("/api/error", 0),    # Ruta /api/error inicialmente con 0 peticiones
    ("/health", 0)        # Ruta /health inicialmente con 0 peticiones
]

TOTAL_REQUESTS = 4500  # Total de peticiones que queremos hacer

def distribute_requests():
    """Distribuye aleatoriamente las peticiones entre las rutas"""
    remaining_requests = TOTAL_REQUESTS
    while remaining_requests > 0:
        # Elige una ruta aleatoria
        route, current_count = random.choice(ROUTES)
        
        # Si aún no hemos alcanzado el total de peticiones, asignamos una
        if remaining_requests > 0:
            ROUTES[ROUTES.index((route, current_count))] = (route, current_count + 1)
            remaining_requests -= 1

def test_route(route):
    """Función que hace una petición GET a una ruta específica"""
    try:
        response = requests.get(f"{BASE_URL}{route}")
        return (route, response.status_code, response.json())
    except requests.exceptions.RequestException as e:
        return (route, "Error", str(e))

def main():
    """Llama a cada ruta la cantidad especificada de veces"""
    distribute_requests()  # Distribuye las 500 peticiones aleatoriamente entre las rutas

    all_requests = []
    for route, times in ROUTES:
        if times > 0:
            all_requests.extend([route] * times)

    # Realiza las peticiones de forma paralela
    with ThreadPoolExecutor(max_workers=45) as executor:
        future_to_route = {executor.submit(test_route, route): route for route in all_requests}
        
        # Muestra el progreso de las peticiones
        for future in tqdm(as_completed(future_to_route), total=len(all_requests), desc="Progreso de peticiones"):
            route, status, response = future.result()
            #print(f"Respuesta de {route}: {status} - {response}")

if __name__ == "__main__":
    main()
