import sys
import json
sys.path.insert(0, 'backend')

from api.services import compute_chart

# Test para verificar que Lilith está en la respuesta
payload = {
    "datetime": "1992-07-12T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "placidus",
    "topocentric_moon_only": False
}

result = compute_chart(payload, 'se_data')

print("="*70)
print("VERIFICACIÓN: ¿LILITH ESTÁ EN LA RESPUESTA?")
print("="*70)

# Verificar que Lilith existe
if 'lilith' in result['planets']:
    print("\n✅ SÍ - Lilith está incluida en la respuesta\n")
    
    lilith_data = result['planets']['lilith']
    print("INFORMACIÓN DE LILITH:")
    print(f"  Posición (value): {lilith_data['value']:.4f}°")
    print(f"  Velocidad (speed): {lilith_data['speed']:.6f}°/día")
    print(f"  Retrógrado: {lilith_data['retrograde']}")
    print(f"  Formato legible: {lilith_data['formatted']}")
    
    print("\n" + "="*70)
    print("TODOS LOS PLANETAS EN LA RESPUESTA:")
    print("="*70)
    
    for i, (nombre, data) in enumerate(result['planets'].items(), 1):
        retro = " ℞" if data['retrograde'] else ""
        print(f"{i:2}. {nombre.upper():12} - {data['formatted']}{retro}")
    
    print(f"\nTotal de planetas: {len(result['planets'])}")
    
    # Mostrar también aspectos que incluyen a Lilith
    print("\n" + "="*70)
    print("ASPECTOS QUE INCLUYEN A LILITH:")
    print("="*70)
    
    lilith_aspects = [
        asp for asp in result['aspects'] 
        if 'lilith' in [asp['planet_a'], asp['planet_b']]
    ]
    
    if lilith_aspects:
        for asp in lilith_aspects:
            print(f"  {asp['planet_a'].upper()} - {asp['planet_b'].upper()}: {asp['aspect']} ({asp['angle']:.1f}°, orb {asp['orb']:.1f}°)")
    else:
        print("  No hay aspectos con Lilith en esta carta")
    
else:
    print("\n❌ NO - Lilith NO está en la respuesta")
    print("Planetas disponibles:", list(result['planets'].keys()))

print("\n" + "="*70)
print("RESPUESTA JSON COMPLETA (primeros planetas):")
print("="*70)
print(json.dumps({
    'planets': {
        k: v for k, v in list(result['planets'].items())[:3]
    },
    'lilith': result['planets'].get('lilith', 'NO ENCONTRADA')
}, indent=2, ensure_ascii=False))
