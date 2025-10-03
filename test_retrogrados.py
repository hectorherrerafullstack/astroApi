import sys
sys.path.insert(0, 'backend')

from api.services import compute_chart

# Datos de Tegucigalpa
payload = {
    "datetime": "1992-07-12T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "placidus",
    "topocentric_moon_only": False
}

ephe_path = "se_data"
result = compute_chart(payload, ephe_path)

print("\n=== PLANETAS RETRÓGRADOS ===")
planetas_retrogrados = {
    nombre: info 
    for nombre, info in result['planets'].items() 
    if info.get('retrograde', False)
}

if planetas_retrogrados:
    for nombre, info in planetas_retrogrados.items():
        print(f"{nombre.capitalize()}: {info['formatted']} (velocidad: {info['speed']:.4f}°/día)")
else:
    print("No hay planetas retrógrados en esta carta")

print(f"\nTotal de planetas retrógrados: {len(planetas_retrogrados)}")

print("\n=== TODOS LOS PLANETAS ===")
for nombre, info in result['planets'].items():
    estado = "RETRÓGRADO ℞" if info['retrograde'] else "Directo"
    print(f"{nombre.capitalize()}: {info['formatted']:30} - {estado}")
