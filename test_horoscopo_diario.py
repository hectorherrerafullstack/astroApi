"""
Script de prueba para el sistema de horóscopo diario.
Usa la carta natal de Tegucigalpa como ejemplo.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from datetime import datetime, timedelta
from api.services import compute_chart
from api.horoscope_service import generate_daily_horoscope_personal, calculate_transits

# Carta natal ejemplo (Tegucigalpa, 7 dic 1992, 23:58)
BIRTH_DATA = {
    "datetime": "1992-12-07T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "P",
    "topocentric_moon_only": False
}

def test_transits():
    """Prueba el cálculo de tránsitos para hoy"""
    print("\n" + "="*80)
    print("🌟 TRÁNSITOS DEL DÍA")
    print("="*80)
    
    hoy = datetime.now()
    transits = calculate_transits(hoy, "America/Tegucigalpa")
    
    print(f"\nFecha: {hoy.strftime('%Y-%m-%d %H:%M')}")
    print(f"Zona horaria: America/Tegucigalpa\n")
    
    print("Posiciones planetarias actuales:")
    print("-" * 80)
    for planet, data in transits.items():
        retrograde = " ℞" if data["speed"] < 0 else ""
        print(f"{planet.capitalize():12} | {data['sign']:12} | "
              f"{data['degree_in_sign']:5.2f}° | {data['longitude']:7.3f}°{retrograde}")
    
    return transits


def test_daily_horoscope():
    """Prueba el horóscopo diario completo"""
    print("\n" + "="*80)
    print("📅 HORÓSCOPO DIARIO PERSONALIZADO")
    print("="*80)
    
    # Primero calculamos la carta natal
    print("\n1. Calculando carta natal...")
    se_data_path = os.path.join(os.path.dirname(__file__), 'se_data')
    natal_chart = compute_chart(BIRTH_DATA, se_data_path)
    
    # Simplificar birth_data para el horóscopo
    birth_data_simplified = {
        "planets": natal_chart["planets"],
        "houses": natal_chart["houses"]
    }
    
    # Calcular horóscopo para hoy
    print("2. Calculando tránsitos y aspectos para hoy...")
    hoy = datetime.now()
    horoscope = generate_daily_horoscope_personal(
        birth_data_simplified,
        target_date=hoy,
        timezone="America/Tegucigalpa"
    )
    
    print(f"\n📆 Horóscopo para: {horoscope['date']}")
    print(f"🌅 Ascendente natal: {horoscope['natal_ascendant']}")
    
    # Mostrar aspectos principales
    print("\n" + "="*80)
    print("⭐ ASPECTOS MÁS IMPORTANTES DEL DÍA")
    print("="*80)
    
    if horoscope['top_aspects']:
        for i, aspect in enumerate(horoscope['top_aspects'], 1):
            applying = "📈 Aplicativo" if aspect['applying'] else "📉 Separativo"
            print(f"\n{i}. {aspect['transit_planet'].upper()} → {aspect['natal_planet'].upper()}")
            print(f"   Aspecto: {aspect['aspect']}")
            print(f"   Orbe: {aspect['orb']:.2f}°")
            print(f"   {applying}")
            print(f"   Peso: {'⭐' * min(aspect['weight'] // 3, 5)}")
    else:
        print("No hay aspectos mayores exactos hoy.")
    
    # Mostrar casas activadas
    print("\n" + "="*80)
    print("🏠 CASAS NATALES ACTIVADAS POR TRÁNSITOS")
    print("="*80)
    
    for house_data in horoscope['houses_activated']:
        house_num = house_data['house']
        planets = [p['planet'].capitalize() for p in house_data['planets']]
        print(f"\nCasa {house_num}: {', '.join(planets)}")
    
    # Interpretación
    print("\n" + "="*80)
    print("📖 INTERPRETACIÓN DEL DÍA")
    print("="*80)
    print(horoscope['interpretation']['summary'])
    
    print("\n" + "="*80)
    print("💡 CONSEJO DEL DÍA")
    print("="*80)
    print(horoscope['interpretation']['advice'])
    
    print("\n" + "="*80)


def test_manana():
    """Prueba el horóscopo para mañana"""
    print("\n" + "="*80)
    print("🔮 PREVISUALIZACIÓN: MAÑANA")
    print("="*80)
    
    se_data_path = os.path.join(os.path.dirname(__file__), 'se_data')
    natal_chart = compute_chart(BIRTH_DATA, se_data_path)
    birth_data_simplified = {
        "planets": natal_chart["planets"],
        "houses": natal_chart["houses"]
    }
    
    manana = datetime.now() + timedelta(days=1)
    horoscope = generate_daily_horoscope_personal(
        birth_data_simplified,
        target_date=manana,
        timezone="America/Tegucigalpa"
    )
    
    print(f"\n📆 Fecha: {horoscope['date']}")
    print(f"\nTop 3 aspectos:")
    for i, aspect in enumerate(horoscope['top_aspects'][:3], 1):
        print(f"{i}. {aspect['transit_planet'].upper()} {aspect['aspect']} "
              f"{aspect['natal_planet'].upper()} (orbe: {aspect['orb']:.2f}°)")
    
    print(f"\n💡 {horoscope['interpretation']['advice']}")


if __name__ == "__main__":
    try:
        # Probar tránsitos
        test_transits()
        
        # Probar horóscopo completo
        test_daily_horoscope()
        
        # Probar mañana
        test_manana()
        
        print("\n✅ Todas las pruebas completadas exitosamente!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
