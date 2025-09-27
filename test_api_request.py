import requests

# URL de la API en Koyeb (reemplaza con tu URL real)
API_URL = "https://astroapi-hector.koyeb.app/api/compute/"

# Datos de ejemplo para la request (cambia con tus datos)
payload = {
    "datetime": "1992-02-14T20:30:00",
    "timezone": "Europe/Madrid",
    "latitude": 41.5467,
    "longitude": 2.1094,
    "house_system": "placidus",
    "topocentric_moon_only": False
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Hacer la request POST
try:
    response = requests.post(API_URL, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Respuesta exitosa:")
        print(f"Planetas: {len(data.get('planets', {}))} calculados")
        print(f"Casas: Asc {data.get('houses', {}).get('asc', {}).get('value', 'N/A'):.1f}°, MC {data.get('houses', {}).get('mc', {}).get('value', 'N/A'):.1f}°")
        print(f"Aspectos encontrados: {len(data.get('aspects', []))}")
        # Mostrar algunos aspectos
        aspects = data.get('aspects', [])
        if aspects:
            print("Ejemplos de aspectos:")
            for asp in aspects[:3]:  # primeros 3
                print(f"  {asp['a']} - {asp['b']}: {asp['aspect']} ({asp['angle']:.1f}°, orb {asp['orb']:.1f}°)")
        print(f"JD_UT: {data.get('meta', {}).get('jd_ut', 'N/A')}")
    else:
        print(f"Error: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error de conexión: {e}")

# También puedes probar el health check
health_url = "https://astroapi-hector.koyeb.app/api/health/"
try:
    health_response = requests.get(health_url)
    print(f"\nHealth Check - Status: {health_response.status_code}")
    if health_response.status_code == 200:
        print("API funcionando correctamente")
    else:
        print(f"Health check falló: {health_response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error en health check: {e}")