#!/usr/bin/env python
"""
Script de prueba para comparar posiciones calculadas con valores de referencia.
Ejecuta: python test_chart.py

Requiere que pyswisseph esté instalado y los archivos de efemérides en se_data/.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from api.services import compute_chart

# Valores de referencia (ejemplo para Persona 1 - Terrassa)
# Estos son valores aproximados; ajusta con valores reales de Astro.com o Swiss Ephemeris
REFERENCE = {
    "sun": 224.5,  # Escorpio 14°
    "moon": 135.2,  # Leo 15° (topocéntrico)
    "asc": 180.0,  # Libra 0°
    "mc": 90.0,    # Cáncer 0°
}

def test_chart():
    payload = {
        "datetime": "1997-11-06T14:05:00",
        "timezone": "Europe/Madrid",
        "latitude": 41.5629623,
        "longitude": 2.0100492,
        "house_system": "placidus",
        "topocentric_moon_only": True
    }

    ephe_path = os.path.join(os.path.dirname(__file__), 'se_data')
    result = compute_chart(payload, ephe_path)

    print("Resultados calculados:")
    print(f"Sun: {result['planets']['sun']['longitude']:.1f}°")
    print(f"Moon: {result['planets']['moon']['longitude']:.1f}°")
    print(f"Asc: {result['houses']['asc']['value']:.1f}°")
    print(f"MC: {result['houses']['mc']['value']:.1f}°")

    # Comparar con referencia
    tolerance = 0.1  # grados
    errors = []

    for key, ref in REFERENCE.items():
        if key in result['planets']:
            calc = result['planets'][key]['longitude']
        elif key in result['houses']:
            calc = result['houses'][key]['value']
        else:
            continue

        diff = abs(calc - ref)
        if diff > tolerance:
            errors.append(f"{key}: calculado {calc:.1f}°, referencia {ref:.1f}°, diferencia {diff:.1f}°")
        else:
            print(f"✓ {key}: OK")

    if errors:
        print("\nErrores encontrados:")
        for error in errors:
            print(f"✗ {error}")
        return False
    else:
        print("\n✓ Todos los valores dentro de la tolerancia.")
        return True

if __name__ == "__main__":
    success = test_chart()
    sys.exit(0 if success else 1)