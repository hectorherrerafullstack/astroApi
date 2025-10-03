# Test simple de la carta de Tegucigalpa sin Django test framework
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api.services import compute_chart

def test_tegucigalpa():
    ephe_path = os.path.join(os.path.dirname(__file__), 'se_data')
    
    payload = {
        "datetime": "1992-07-12T23:58:00",
        "timezone": "America/Tegucigalpa",
        "latitude": 14.0723,
        "longitude": -87.1921,
        "house_system": "placidus",
        "topocentric_moon_only": False
    }
    
    result = compute_chart(payload, ephe_path)
    
    print("\n=== CARTA ASTRAL: Tegucigalpa 12/07/1992 23:58 ===\n")
    
    print("PLANETAS:")
    for planet, data in result['planets'].items():
        retro = " ℞ (RETRÓGRADO)" if data['retrograde'] else " (Directo)"
        print(f"  {planet.upper()}: {data['formatted']}{retro}")
        print(f"    Velocidad: {data['speed']:.4f}°/día")
    
    print(f"\nCASAS:")
    print(f"  ASCENDENTE: {result['houses']['ascendente']['formatted']}")
    print(f"  MEDIO CIELO: {result['houses']['mc']['formatted']}")
    
    print(f"\n  Cúspides:")
    for cusp in result['houses']['cusps']:
        print(f"    Casa {cusp['house']}: {cusp['formatted']}")
    
    print(f"\nASPECTOS ENCONTRADOS: {len(result['aspects'])}")
    if result['aspects']:
        print("\nPrimeros 10 aspectos:")
        for i, asp in enumerate(result['aspects'][:10], 1):
            print(f"  {i}. {asp['planet_a'].upper()} - {asp['planet_b'].upper()}: {asp['aspect']} ({asp['angle']:.1f}°, orbe {asp['orb']:.1f}°)")
    
    print(f"\nMETADATA:")
    print(f"  Julian Day (UT): {result['jd_ut']}")
    print(f"  Sistema de casas: {result['meta']['house_system']}")
    
    return result

if __name__ == "__main__":
    test_tegucigalpa()
