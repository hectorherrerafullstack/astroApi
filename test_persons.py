#!/usr/bin/env python
"""
Script para probar las posiciones calculadas contra los valores proporcionados.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from api.services import compute_chart

# Configurar path de efemérides
ephe_path = os.path.join(os.path.dirname(__file__), 'se_data')

# Datos de las personas
persons = [
    {
        "name": "Persona 1",
        "datetime": "1997-11-06T14:05:00",
        "timezone": "Europe/Madrid",
        "latitude": 41.5629623,
        "longitude": 2.0100492,
        "house_system": "placidus",
        "topocentric_moon_only": False
    },
    {
        "name": "Persona 2",
        "datetime": "1992-02-14T20:30:00",
        "timezone": "Europe/Madrid",
        "latitude": 41.5467,  # Sabadell exact
        "longitude": 2.1094,
        "house_system": "placidus",
        "topocentric_moon_only": False
    },
    {
        "name": "Persona 3",
        "datetime": "1972-11-30T08:30:00",
        "timezone": "Europe/Madrid",
        "latitude": 40.4168,  # Madrid
        "longitude": -3.7038,
        "house_system": "placidus",
        "topocentric_moon_only": False
    },
    {
        "name": "Persona 4",
        "datetime": "1981-10-16T14:00:00",
        "timezone": "Europe/Madrid",
        "latitude": 41.9794,  # Girona
        "longitude": 2.8214,
        "house_system": "placidus",
        "topocentric_moon_only": False
    }
]

def print_results(result, name):
    print(f"\n{name}:")
    print(f"Sun: {result['planets']['sun']['formatted']}")
    print(f"Moon: {result['planets']['moon']['formatted']}")
    print(f"Mercury: {result['planets']['mercury']['formatted']}")
    print(f"Venus: {result['planets']['venus']['formatted']}")
    print(f"Mars: {result['planets']['mars']['formatted']}")
    print(f"Jupiter: {result['planets']['jupiter']['formatted']}")
    print(f"Saturn: {result['planets']['saturn']['formatted']}")
    print(f"Uranus: {result['planets']['uranus']['formatted']}")
    print(f"Neptune: {result['planets']['neptune']['formatted']}")
    print(f"Pluto: {result['planets']['pluto']['formatted']}")
    print(f"Asc: {result['houses']['asc']['formatted']}")
    print(f"MC: {result['houses']['mc']['formatted']}")
    print(f"True Node: {result['planets']['true_node']['formatted']}")
    print(f"Chiron: {result['planets']['chiron']['formatted']}")

if __name__ == "__main__":
    for person in persons:
        result = compute_chart(person, ephe_path)
        print_results(result, person["name"])