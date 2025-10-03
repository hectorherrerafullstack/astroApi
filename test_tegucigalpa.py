# Test directo del servicio sin Django test
from backend.api.services import compute_chart
from django.conf import settings
import os
import sys

# Configurar path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django settings mínimo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

def test_tegucigalpa():
    payload = {
        "datetime": "1992-07-12T23:58:00",
        "timezone": "America/Tegucigalpa",
        "latitude": 14.0723,
        "longitude": -87.1921,
        "house_system": "placidus",
        "topocentric_moon_only": False
    }
    
    result = compute_chart(payload, settings.SE_EPHE_PATH)
    
    print("\n=== Tegucigalpa 12/07/1992 23:58 ===")
    print(f"Sol: {result['planets']['sun']['formatted']} (Retrógrado: {result['planets']['sun']['retrograde']})")
    print(f"Luna: {result['planets']['moon']['formatted']} (Retrógrado: {result['planets']['moon']['retrograde']})")
    print(f"Mercurio: {result['planets']['mercury']['formatted']} (Retrógrado: {result['planets']['mercury']['retrograde']})")
    print(f"Ascendente: {result['houses']['ascendente']['formatted']}")
    print(f"MC: {result['houses']['mc']['formatted']}")
    print(f"Lilith: {result['planets']['lilith']['formatted']} (Retrógrado: {result['planets']['lilith']['retrograde']})")
    print(f"\nAspectos encontrados: {len(result['aspects'])}")
    
    if result['aspects']:
        print("\nPrimeros 5 aspectos:")
        for asp in result['aspects'][:5]:
            print(f"  {asp['planet_a']} - {asp['planet_b']}: {asp['aspect']} ({asp['angle']:.1f}°, orb {asp['orb']:.1f}°)")
    
    return result

if __name__ == "__main__":
    test_tegucigalpa()
