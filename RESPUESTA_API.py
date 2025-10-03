"""
DOCUMENTACIÓN DE LA RESPUESTA DEL ENDPOINT /api/compute/

Cuando haces un POST a /api/compute/ con este payload:

{
  "datetime": "1992-07-12T23:58:00",
  "timezone": "America/Tegucigalpa",
  "latitude": 14.0723,
  "longitude": -87.1921,
  "house_system": "placidus",
  "topocentric_moon_only": false
}

RECIBES ESTA RESPUESTA COMPLETA:
"""

RESPUESTA_EJEMPLO = {
  "jd_ut": 2448816.748616339,  # Julian Day (UT)
  
  # ======== PLANETAS ========
  "planets": {
    "sun": {
      "value": 111.089,              # Longitud eclíptica (0-360°)
      "speed": 0.9534,               # Velocidad diaria (°/día)
      "retrograde": False,           # ¿Está retrógrado?
      "formatted": "Cáncer 21° 5' 22\""  # Formato legible
    },
    "moon": {
      "value": 273.910,
      "speed": 12.1521,
      "retrograde": False,
      "formatted": "Capricornio 3° 54' 37\""
    },
    "mercury": {
      "value": 135.668,
      "speed": 0.5171,
      "retrograde": False,           # Mercury NO retrógrado
      "formatted": "Leo 15° 40' 6\""
    },
    "venus": {
      "value": 119.224,
      "speed": 1.2296,
      "retrograde": False,
      "formatted": "Cáncer 29° 13' 27\""
    },
    "mars": {
      "value": 50.622,
      "speed": 0.7026,
      "retrograde": False,
      "formatted": "Tauro 20° 37' 18\""
    },
    "jupiter": {
      "value": 161.713,
      "speed": 0.1709,
      "retrograde": False,
      "formatted": "Virgo 11° 42' 47\""
    },
    "saturn": {
      "value": 316.920,
      "speed": -0.0630,              # Velocidad NEGATIVA = retrógrado
      "retrograde": True,            # ¡SATURNO RETRÓGRADO!
      "formatted": "Acuario 16° 55' 12\" ℞"  # Símbolo ℞ incluido
    },
    "uranus": {
      "value": 285.817,
      "speed": -0.0401,
      "retrograde": True,            # ¡URANO RETRÓGRADO!
      "formatted": "Capricornio 15° 49' 3\" ℞"
    },
    "neptune": {
      "value": 287.473,
      "speed": -0.0269,
      "retrograde": True,            # ¡NEPTUNO RETRÓGRADO!
      "formatted": "Capricornio 17° 28' 21\" ℞"
    },
    "pluto": {
      "value": 230.234,
      "speed": -0.0096,
      "retrograde": True,            # ¡PLUTÓN RETRÓGRADO!
      "formatted": "Escorpio 20° 14' 3\" ℞"
    },
    "chiron": {
      "value": 130.452,
      "speed": 0.1198,
      "retrograde": False,
      "formatted": "Leo 10° 27' 7\""
    },
    "true_node": {
      "value": 270.697,
      "speed": -0.0042,
      "retrograde": True,            # ¡NODO VERDADERO RETRÓGRADO!
      "formatted": "Capricornio 0° 41' 48\" ℞"
    },
    "lilith": {                      # ¡LILITH INCLUIDA!
      "value": 319.308,
      "speed": 0.1115,
      "retrograde": False,
      "formatted": "Acuario 19° 18' 27\""
    }
  },
  
  # ======== CASAS ========
  "houses": {
    "ascendente": {                  # ¡ASCENDENTE!
      "value": 28.475,
      "formatted": "Aries 28° 28' 31\""
    },
    "asc": {                         # Alias (mismo valor)
      "value": 28.475,
      "formatted": "Aries 28° 28' 31\""
    },
    "mc": {                          # ¡MEDIO CIELO!
      "value": 291.919,
      "formatted": "Capricornio 21° 55' 9\""
    },
    "cusps": [                       # 12 cúspides
      {"house": 1, "value": 28.475, "formatted": "Aries 28° 28' 31\""},
      {"house": 2, "value": 59.381, "formatted": "Tauro 29° 22' 51\""},
      {"house": 3, "value": 86.104, "formatted": "Géminis 26° 6' 16\""},
      {"house": 4, "value": 111.919, "formatted": "Cáncer 21° 55' 9\""},
      {"house": 5, "value": 140.006, "formatted": "Leo 20° 0' 19\""},
      {"house": 6, "value": 172.583, "formatted": "Virgo 22° 34' 58\""},
      {"house": 7, "value": 208.475, "formatted": "Libra 28° 28' 31\""},
      {"house": 8, "value": 239.381, "formatted": "Escorpio 29° 22' 51\""},
      {"house": 9, "value": 266.104, "formatted": "Sagitario 26° 6' 16\""},
      {"house": 10, "value": 291.919, "formatted": "Capricornio 21° 55' 9\""},
      {"house": 11, "value": 320.006, "formatted": "Acuario 20° 0' 19\""},
      {"house": 12, "value": 352.583, "formatted": "Piscis 22° 34' 58\""}
    ]
  },
  
  # ======== ASPECTOS ========
  "aspects": [
    {
      "planet_a": "sun",
      "planet_b": "mars",
      "aspect": "Sextile",
      "angle": 60.467,               # Ángulo exacto entre planetas
      "orb": 0.467                   # Diferencia con aspecto perfecto
    },
    {
      "planet_a": "sun",
      "planet_b": "uranus",
      "aspect": "Opposition",
      "angle": 174.728,
      "orb": 5.272
    },
    {
      "planet_a": "mercury",
      "planet_b": "saturn",
      "aspect": "Opposition",
      "angle": 178.748,
      "orb": 1.252
    },
    {
      "planet_a": "moon",
      "planet_b": "true_node",
      "aspect": "Conjunction",
      "angle": 3.213,
      "orb": 3.213
    }
    # ... más aspectos (27 en total en este ejemplo)
  ],
  
  # ======== METADATA ========
  "meta": {
    "ephe_path": "C:\\...\\se_data",
    "flags": 258,                    # Flags de Swiss Ephemeris
    "house_system": "placidus"
  }
}

"""
CÓMO USAR LA RESPUESTA:

1. FILTRAR PLANETAS RETRÓGRADOS:
   retrogrados = [p for p, data in response['planets'].items() if data['retrograde']]
   # Resultado: ['saturn', 'uranus', 'neptune', 'pluto', 'true_node']

2. OBTENER ASCENDENTE Y MC:
   asc = response['houses']['ascendente']['formatted']  # "Aries 28° 28' 31""
   mc = response['houses']['mc']['formatted']           # "Capricornio 21° 55' 9""

3. OBTENER LILITH:
   lilith = response['planets']['lilith']['formatted']  # "Acuario 19° 18' 27""

4. CONTAR ASPECTOS:
   total_aspectos = len(response['aspects'])  # 27

5. VERIFICAR SI UN PLANETA ES RETRÓGRADO:
   mercurio_retro = response['planets']['mercury']['retrograde']  # False
   saturno_retro = response['planets']['saturn']['retrograde']    # True

6. OBTENER VELOCIDADES:
   velocidad_luna = response['planets']['moon']['speed']  # 12.1521 °/día
"""

print(__doc__)
print("\n" + "="*70)
print("EJEMPLO DE ESTRUCTURA DE RESPUESTA:")
print("="*70)

import json
print(json.dumps(RESPUESTA_EJEMPLO, indent=2, ensure_ascii=False))
