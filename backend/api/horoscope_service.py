# This file is part of astroapi.
#
# astroapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import swisseph as swe
from datetime import datetime, date
from dateutil import tz
from pathlib import Path
import math
import os
from .cache_manager import cache_transits, cache_daily_horoscope, measure_performance

# Configuración robusta de path de efemérides
# 1. Intentar variable de entorno (Docker/Koyeb)
ephe_path = os.environ.get("SE_EPHE_PATH")

# 2. Fallback: cálculo relativo (Local dev)
if not ephe_path:
    BASE_DIR = Path(__file__).resolve().parents[1]
    ephe_path = str(BASE_DIR.parent / "se_data")

swe.set_ephe_path(ephe_path)
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

# Planetas para tránsitos (rápidos más influyentes en lo diario)
TRANSIT_PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
}

# Planetas rápidos (más peso en horóscopos diarios)
FAST_PLANETS = ["moon", "mercury", "venus", "mars"]
SLOW_PLANETS = ["jupiter", "saturn", "uranus", "neptune", "pluto"]

# Signos
SIGNS = ['aries', 'tauro', 'geminis', 'cancer', 'leo', 'virgo',
         'libra', 'escorpio', 'sagitario', 'capricornio', 'acuario', 'piscis']

SIGNS_ES = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

# Significado de casas
HOUSES_MEANING = {
    1: 'identidad y apariencia',
    2: 'dinero y recursos',
    3: 'comunicación y hermanos',
    4: 'hogar y familia',
    5: 'amor y creatividad',
    6: 'trabajo y salud',
    7: 'pareja y asociaciones',
    8: 'transformación y recursos compartidos',
    9: 'estudios y viajes',
    10: 'carrera y reputación',
    11: 'amistades y proyectos',
    12: 'espiritualidad y descanso'
}

# Aspectos con orbes (más generosos para horóscopos diarios)
ASPECTS_CONFIG = [
    {"name": "Conjunción", "angle": 0, "orb_fast": 8, "orb_slow": 6},
    {"name": "Sextil", "angle": 60, "orb_fast": 6, "orb_slow": 4},
    {"name": "Cuadratura", "angle": 90, "orb_fast": 7, "orb_slow": 5},
    {"name": "Trígono", "angle": 120, "orb_fast": 8, "orb_slow": 6},
    {"name": "Oposición", "angle": 180, "orb_fast": 8, "orb_slow": 6},
]


def to_jd_ut(dt: datetime, tzname: str = "UTC") -> float:
    """Convierte datetime a Julian Day UT"""
    zone = tz.gettz(tzname)
    if zone:
        dt_local = dt.replace(tzinfo=zone)
        dt_utc = dt_local.astimezone(tz.UTC)
    else:
        dt_utc = dt
    
    jd_et, jd_ut = swe.utc_to_jd(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour, dt_utc.minute, dt_utc.second,
        swe.GREG_CAL
    )
    return jd_ut


def get_moon_realtime(dt: datetime, tzname: str = "UTC") -> dict:
    """
    Calcula la posición de la Luna en TIEMPO REAL sin caché.
    Usar para el endpoint /api/moon/ donde se necesita precisión al minuto.
    """
    jd_ut = to_jd_ut(dt, tzname)
    
    lonlat, ret = swe.calc_ut(jd_ut, swe.MOON, FLAGS)
    moon_lon = lonlat[0] % 360.0
    moon_speed = lonlat[3]
    
    # Calcular posición del Sol para la fase
    sun_lonlat, _ = swe.calc_ut(jd_ut, swe.SUN, FLAGS)
    sun_lon = sun_lonlat[0] % 360.0
    
    # Calcular fase lunar
    angle = (moon_lon - sun_lon) % 360
    
    # Definir ventanas precisas (±10 grados para fases principales)
    if angle < 10 or angle > 350:
        phase = "Luna Nueva"
    elif angle < 80:
        phase = "Luna Creciente"  # Waxing Crescent
    elif angle < 100:
        phase = "Cuarto Creciente"
    elif angle < 170:
        phase = "Gibosa Creciente"  # Waxing Gibbous
    elif angle < 190:
        phase = "Luna Llena"
    elif angle < 260:
        phase = "Gibosa Menguante"  # Waning Gibbous
    elif angle < 280:
        phase = "Cuarto Menguante"
    else:
        phase = "Luna Menguante"    # Waning Crescent
        
    # Calcular porcentaje de iluminación
    # (1 - cos(angulo)) / 2 * 100
    import math
    illumination = (1 - math.cos(math.radians(angle))) / 2 * 100
    
    return {
        "longitude": moon_lon,
        "speed": moon_speed,
        "sign": SIGNS_ES[int(moon_lon // 30)],
        "sign_index": int(moon_lon // 30),
        "degree_in_sign": moon_lon % 30,
        "phase": phase,
        "phase_angle": angle,
        "illumination": round(illumination, 1)
    }


@cache_transits(ttl=3600)  # Caché de 1 hora para tránsitos
@measure_performance("calculate_transits")
def calculate_transits(dt: datetime, tzname: str = "UTC") -> dict:
    """Calcula posiciones planetarias para una fecha/hora (tránsitos)"""
    jd_ut = to_jd_ut(dt, tzname)
    transits = {}
    
    for name, pid in TRANSIT_PLANETS.items():
        lonlat, ret = swe.calc_ut(jd_ut, pid, FLAGS)
        lon = lonlat[0] % 360.0
        speed = lonlat[3]
        
        transits[name] = {
            "longitude": lon,
            "speed": speed,
            "sign": SIGNS_ES[int(lon // 30)],
            "sign_index": int(lon // 30),
            "degree_in_sign": lon % 30
        }
    
    # Calcular fase lunar
    if "sun" in transits and "moon" in transits:
        sun_lon = transits["sun"]["longitude"]
        moon_lon = transits["moon"]["longitude"]
        angle = (moon_lon - sun_lon) % 360
        
        if angle < 45:
            phase = "Luna Nueva"
        elif angle < 90:
            phase = "Creciente Menguante"
        elif angle < 135:
            phase = "Cuarto Creciente"
        elif angle < 180:
            phase = "Creciente Gibosa"
        elif angle < 225:
            phase = "Luna Llena"
        elif angle < 270:
            phase = "Menguante Gibosa"
        elif angle < 315:
            phase = "Cuarto Menguante"
        else:
            phase = "Menguante Creciente"
        
        transits["moon"]["phase"] = phase
        transits["moon"]["phase_angle"] = angle
    
    return transits


def get_next_moon_ingress(dt: datetime, tzname: str = "UTC") -> dict:
    """
    Encuentra el próximo cambio de signo de la Luna.
    Busca hora por hora y luego refina al minuto.
    """
    jd_ut = to_jd_ut(dt, tzname)
    
    # Posición inicial
    lonlat, ret = swe.calc_ut(jd_ut, swe.MOON, FLAGS)
    start_sign_index = int(lonlat[0] // 30)
    
    current_jd = jd_ut
    # Buscamos en pasos de 1 hora hasta 4 días (por si acaso)
    for _ in range(96):
        current_jd += 1/24.0 # +1 hora
        lonlat, ret = swe.calc_ut(current_jd, swe.MOON, FLAGS)
        current_sign_index = int(lonlat[0] // 30)
        
        if current_sign_index != start_sign_index:
            # Refinar el momento exacto (búsqueda lineal de a 1 minuto)
            # Volvemos atrás la hora que acabamos de saltar
            current_jd -= 1/24.0
            for _ in range(60):
                current_jd += 1/(24.0 * 60.0) # +1 minuto
                lonlat_fine, ret = swe.calc_ut(current_jd, swe.MOON, FLAGS)
                fine_sign_index = int(lonlat_fine[0] // 30)
                if fine_sign_index != start_sign_index:
                    # Encontrado al minuto exacto
                    break
            
            # Convertir JD a UTC datetime
            y, m, d, h = swe.revjul(current_jd, swe.GREG_CAL)
            hours = int(h)
            remainder = (h - hours) * 60
            minutes = int(remainder)
            seconds = int((remainder - minutes) * 60)
            
            # Limpieza básica para evitar micro-errores de precisión
            if seconds >= 60: seconds = 59
            if minutes >= 60: minutes = 59
            
            change_dt = datetime(y, m, d, hours, minutes, seconds)
            
            return {
                "next_sign": SIGNS_ES[current_sign_index],
                "next_sign_index": current_sign_index,
                "change_datetime": change_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "change_iso": change_dt.isoformat() + "Z"
            }
    
    return None


def angular_distance(lon1: float, lon2: float) -> float:
    """Calcula distancia angular entre dos longitudes (0-180°)"""
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff


def find_aspects_to_natal(transits: dict, natal_planets: dict) -> list:
    """
    Encuentra aspectos entre tránsitos y planetas natales.
    
    Args:
        transits: dict con planetas en tránsito
        natal_planets: dict con planetas natales (mismo formato que transits)
    
    Returns:
        lista de aspectos encontrados
    """
    aspects = []
    
    for transit_name, transit_data in transits.items():
        is_fast = transit_name in FAST_PLANETS
        
        for natal_name, natal_data in natal_planets.items():
            distance = angular_distance(
                transit_data["longitude"],
                natal_data["longitude"]
            )
            
            for asp_config in ASPECTS_CONFIG:
                orb = asp_config["orb_fast"] if is_fast else asp_config["orb_slow"]
                diff = abs(distance - asp_config["angle"])
                
                if diff <= orb:
                    # Determinar si es aplicativo o separativo
                    is_applying = transit_data["speed"] > 0  # simplificado
                    
                    # Peso del aspecto
                    weight = 10 if is_fast else 5
                    if is_applying:
                        weight += 3
                    if asp_config["name"] in ["Trígono", "Sextil"]:
                        weight += 2  # aspectos armónicos
                    
                    aspects.append({
                        "transit_planet": transit_name,
                        "natal_planet": natal_name,
                        "aspect": asp_config["name"],
                        "angle": distance,
                        "orb": diff,
                        "applying": is_applying,
                        "weight": weight
                    })
    
    return sorted(aspects, key=lambda x: x["weight"], reverse=True)


def find_mundane_aspects(transits: dict) -> list:
    """
    Encuentra aspectos entre planetas en tránsito (aspectos mundanos).
    
    Args:
        transits: dict con planetas en tránsito
    
    Returns:
        lista de aspectos encontrados entre los planetas
    """
    aspects = []
    planet_names = list(transits.keys())
    
    # Orden definido para evitar duplicados (A-B vs B-A) y pares (A-A)
    # Iteramos por índices
    for i in range(len(planet_names)):
        p1_name = planet_names[i]
        p1_data = transits[p1_name]
        
        for j in range(i + 1, len(planet_names)):
            p2_name = planet_names[j]
            p2_data = transits[p2_name]
            
            # Calcular distancia
            distance = angular_distance(
                p1_data["longitude"],
                p2_data["longitude"]
            )
            
            # Determinar si alguno es rápido (para orbes)
            is_fast = (p1_name in FAST_PLANETS) or (p2_name in FAST_PLANETS)
            
            for asp_config in ASPECTS_CONFIG:
                orb = asp_config["orb_fast"] if is_fast else asp_config["orb_slow"]
                diff = abs(distance - asp_config["angle"])
                
                if diff <= orb:
                    # Aplicativo/Separativo
                    # Aproximación simple: mirar velocidades relativas
                    # Si el más rápido se acerca al ángulo exacto
                    
                    aspects.append({
                        "planet_1": p1_name,
                        "planet_2": p2_name,
                        "aspect": asp_config["name"],
                        "angle": distance,
                        "orb": diff,
                        # "applying": ... (lógica compleja, se puede omitir o simplificar)
                    })
    
    return aspects


def get_daily_planetary_data(target_date: datetime, timezone: str = "UTC") -> dict:
    """
    Obtiene datos diarios globales (posiciones planetarias y aspectos del día),
    sin referencia a una carta natal personal.
    """
    transits = calculate_transits(target_date, timezone)
    aspects = find_mundane_aspects(transits)
    
    # Formatear la salida para el frontend
    
    # 1. Lista de planetas formateada
    planets_formatted = []
    for name, data in transits.items():
        planets_formatted.append({
            "name": name,
            "sign": data["sign"],
            "degree": float(f"{data['degree_in_sign']:.2f}"),  # redondear
            "retrograde": data["speed"] < 0,
            "longitude": float(f"{data['longitude']:.2f}")
        })
    
    # 2. Lista de aspectos formateada
    aspects_formatted = []
    for asp in aspects:
        aspects_formatted.append({
            "planet_1": asp["planet_1"],
            "planet_2": asp["planet_2"],
            "aspect": asp["aspect"],
            "orb": float(f"{asp['orb']:.2f}")
        })

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "planets": planets_formatted,
        "aspects": aspects_formatted
    }


def find_house_for_planet(planet_lon: float, houses_cusps: list) -> int:
    """
    Encuentra en qué casa está un planeta según las cúspides.
    
    Args:
        planet_lon: longitud del planeta (0-360)
        houses_cusps: lista de 12 cúspides [cusp1, cusp2, ...]
    
    Returns:
        número de casa (1-12)
    """
    for i in range(12):
        cusp_current = houses_cusps[i]
        cusp_next = houses_cusps[(i + 1) % 12]
        
        # Manejar el cruce de 360°->0°
        if cusp_next < cusp_current:
            if planet_lon >= cusp_current or planet_lon < cusp_next:
                return i + 1
        else:
            if cusp_current <= planet_lon < cusp_next:
                return i + 1
    
    return 1  # fallback


@cache_daily_horoscope(ttl=3600 * 6)  # Caché de 6 horas para horóscopos
@measure_performance("generate_daily_horoscope")
def generate_daily_horoscope_personal(
    birth_data: dict,
    target_date: datetime = None,
    timezone: str = "UTC"
) -> dict:
    """
    Genera horóscopo diario personalizado basado en tránsitos sobre carta natal.
    
    Args:
        birth_data: dict con carta natal {
            "planets": {...},  # del endpoint /api/compute/
            "houses": {"cusps": [...]}
        }
        target_date: fecha para calcular tránsitos (default: hoy)
        timezone: zona horaria para tránsitos
    
    Returns:
        dict con interpretación del día
    """
    if target_date is None:
        target_date = datetime.now()
    
    # Calcular tránsitos del día
    transits = calculate_transits(target_date, timezone)
    
    # Extraer planetas natales en formato compatible
    natal_planets = {}
    for name, data in birth_data["planets"].items():
        natal_planets[name] = {
            "longitude": data["value"],
            "sign": SIGNS_ES[int(data["value"] // 30)],
            "sign_index": int(data["value"] // 30)
        }
    
    # Extraer cúspides de casas natales
    natal_cusps = [cusp["value"] for cusp in birth_data["houses"]["cusps"]]
    
    # Encontrar aspectos tránsito-natal
    aspects = find_aspects_to_natal(transits, natal_planets)
    
    # Identificar casas activadas por tránsitos
    houses_activated = {}
    for transit_name, transit_data in transits.items():
        house_num = find_house_for_planet(transit_data["longitude"], natal_cusps)
        if house_num not in houses_activated:
            houses_activated[house_num] = []
        houses_activated[house_num].append({
            "planet": transit_name,
            "is_fast": transit_name in FAST_PLANETS
        })
    
    # Seleccionar top 5 aspectos más importantes
    top_aspects = aspects[:5]
    
    # Seleccionar top 3 casas más activadas (priorizando planetas rápidos)
    houses_priority = []
    for house_num, planets in houses_activated.items():
        weight = sum(5 if p["is_fast"] else 2 for p in planets)
        houses_priority.append({"house": house_num, "weight": weight, "planets": planets})
    
    houses_priority = sorted(houses_priority, key=lambda x: x["weight"], reverse=True)[:3]
    
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "transits": transits,
        "top_aspects": top_aspects,
        "houses_activated": houses_priority,
        "natal_ascendant": birth_data["houses"]["ascendente"]["formatted"],
        "interpretation": generate_interpretation(top_aspects, houses_priority)
    }


def generate_interpretation(aspects: list, houses: list) -> dict:
    """
    Genera interpretación textual del horóscopo diario.
    """
    lines = []
    
    # Interpretación de aspectos principales
    if aspects:
        lines.append("**Aspectos clave del día:**")
        for asp in aspects[:3]:
            line = interpret_aspect(asp)
            lines.append(f"- {line}")
    
    # Interpretación de casas activadas
    if houses:
        lines.append("\n**Áreas de vida en foco:**")
        for house_data in houses:
            house_num = house_data["house"]
            planets_str = ", ".join([p["planet"].capitalize() for p in house_data["planets"]])
            lines.append(
                f"- Casa {house_num} ({HOUSES_MEANING[house_num]}): "
                f"Activada por {planets_str}."
            )
    
    # Consejo general
    consejo = generate_daily_advice(aspects, houses)
    
    return {
        "summary": "\n".join(lines),
        "advice": consejo
    }


def interpret_aspect(aspect: dict) -> str:
    """Interpreta un aspecto individual"""
    transit_p = aspect["transit_planet"].capitalize()
    natal_p = aspect["natal_planet"].capitalize()
    asp_name = aspect["aspect"]
    applying = "aplicativo" if aspect["applying"] else "separativo"
    
    # Plantillas básicas (expande según necesites)
    if asp_name == "Conjunción":
        return f"{transit_p} en conjunción con tu {natal_p} natal ({applying}): energía intensa en esa área."
    elif asp_name == "Trígono":
        return f"{transit_p} en trígono a tu {natal_p} natal: flujo favorable, aprovecha oportunidades."
    elif asp_name == "Sextil":
        return f"{transit_p} en sextil a tu {natal_p} natal: posibilidades si tomas acción."
    elif asp_name == "Cuadratura":
        return f"{transit_p} en cuadratura a tu {natal_p} natal: tensión creativa, ajusta expectativas."
    elif asp_name == "Oposición":
        return f"{transit_p} en oposición a tu {natal_p} natal: busca equilibrio, negocia."
    else:
        return f"{transit_p} aspecta a tu {natal_p} natal."


def generate_daily_advice(aspects: list, houses: list) -> str:
    """Genera consejo diario personalizado"""
    # Detectar tono dominante
    harmonious = sum(1 for a in aspects if a["aspect"] in ["Trígono", "Sextil"])
    challenging = sum(1 for a in aspects if a["aspect"] in ["Cuadratura", "Oposición"])
    
    if harmonious > challenging:
        return "Día favorable para avanzar en tus proyectos. Mantén el foco y confía en el flujo."
    elif challenging > harmonious:
        return "Día de ajustes y paciencia. Evita forzar situaciones; observa y adapta."
    else:
        return "Día mixto: elige una prioridad concreta y mantén flexibilidad en el resto."
