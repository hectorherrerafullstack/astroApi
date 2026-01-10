# This file is part of astroapi.
#
# astroapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# astroapi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with astroapi.  If not, see <https://www.gnu.org/licenses/>.

import swisseph as swe
from datetime import datetime, timedelta, date
from dateutil import tz
from pathlib import Path

# Reutilizamos configuración de services.py
BASE_DIR = Path(__file__).resolve().parents[1]
swe.set_ephe_path(str(BASE_DIR.parent / "se_data"))
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

# Planetas para análisis semanal
PLANETS = {
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

# Asteroides principales (solo Quirón - los demás requieren archivos de efemérides adicionales)
ASTEROIDS = {
    "chiron": swe.CHIRON,
}

# Lilith (Luna Negra Media - SE_MEAN_APOG = 12)
LILITH = {
    "lilith": 12,
}

# Planetas rápidos (priorizados para aspectos)
FAST_PLANETS = ["mercury", "venus", "mars"]

# Planetas de peso/intensidad
HEAVY_PLANETS = ["saturn", "pluto"]

# Planetas lentos externos
OUTER_PLANETS = ["jupiter", "uranus", "neptune"]

# Signos en español
SIGNS_ES = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

# Nombres de planetas en español
PLANET_NAMES_ES = {
    "sun": "Sol",
    "moon": "Luna",
    "mercury": "Mercurio",
    "venus": "Venus",
    "mars": "Marte",
    "jupiter": "Júpiter",
    "saturn": "Saturno",
    "uranus": "Urano",
    "neptune": "Neptuno",
    "pluto": "Plutón",
}

# Nombres de asteroides en español
ASTEROID_NAMES_ES = {
    "chiron": "Quirón",
}

# Nombre de Lilith en español
LILITH_NAMES_ES = {
    "lilith": "Lilith",
}

# Aspectos principales
ASPECTS = [
    {"name": "conjunction", "name_es": "Conjunción", "angle": 0, "orb": 8},
    {"name": "opposition", "name_es": "Oposición", "angle": 180, "orb": 8},
    {"name": "square", "name_es": "Cuadratura", "angle": 90, "orb": 7},
    {"name": "trine", "name_es": "Trígono", "angle": 120, "orb": 7},
]

# Fases lunares principales (las que son "titular")
MAIN_LUNAR_PHASES = {
    "new_moon": {"name": "Luna Nueva", "angle_min": 0, "angle_max": 15, "is_highlight": True},
    "first_quarter": {"name": "Cuarto Creciente", "angle_min": 82, "angle_max": 98, "is_highlight": False},
    "full_moon": {"name": "Luna Llena", "angle_min": 172, "angle_max": 188, "is_highlight": True},
    "last_quarter": {"name": "Cuarto Menguante", "angle_min": 262, "angle_max": 278, "is_highlight": False},
}


def get_week_dates(start_date: date = None) -> tuple:
    """
    Calcula las fechas de lunes a domingo de la semana.
    Si no se especifica fecha, usa la semana actual.
    
    Returns:
        tuple: (monday_date, sunday_date)
    """
    if start_date is None:
        start_date = date.today()
    
    # Encontrar el lunes de la semana
    days_since_monday = start_date.weekday()
    monday = start_date - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    
    return monday, sunday


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


def get_planet_position(jd_ut: float, planet_id: int) -> dict:
    """Obtiene la posición de un planeta con manejo de errores"""
    try:
        lonlat, ret = swe.calc_ut(jd_ut, planet_id, FLAGS)
        lon = lonlat[0] % 360.0
        speed = lonlat[3]
        
        return {
            "longitude": lon,
            "sign_index": int(lon // 30),
            "sign": SIGNS_ES[int(lon // 30)],
            "degree": lon % 30,
            "speed": speed,
            "retrograde": speed < 0,
            "error": None
        }
    except Exception as e:
        print(f"Error calculating planet {planet_id}: {str(e)}")
        # Retornar valores seguros para no romper la ejecución
        return {
            "longitude": 0.0,
            "sign_index": 0,
            "sign": "Error",
            "degree": 0.0,
            "speed": 0.0,
            "retrograde": False,
            "error": str(e)
        }


def get_lunar_phase_events(monday: date, sunday: date) -> dict:
    """
    Detecta la fase lunar principal de la semana.
    Prioriza Luna Nueva y Luna Llena como destacadas.
    """
    main_event = None
    
    current = monday
    while current <= sunday:
        dt = datetime(current.year, current.month, current.day, 12, 0, 0)
        jd_ut = to_jd_ut(dt)
        
        sun_pos = get_planet_position(jd_ut, swe.SUN)
        moon_pos = get_planet_position(jd_ut, swe.MOON)
        
        # Ángulo Luna-Sol
        angle = (moon_pos["longitude"] - sun_pos["longitude"]) % 360
        
        for phase_key, phase_data in MAIN_LUNAR_PHASES.items():
            if phase_data["angle_min"] <= angle <= phase_data["angle_max"]:
                event = {
                    "main_event": phase_data["name"],
                    "date": current.strftime("%Y-%m-%d"),
                    "sign": moon_pos["sign"],
                    "is_highlight": phase_data["is_highlight"]
                }
                # Priorizar Luna Nueva y Luna Llena
                if phase_data["is_highlight"]:
                    return event
                elif main_event is None:
                    main_event = event
        
        current += timedelta(days=1)
    
    # Si no hay evento principal, retornar la fase del inicio de semana
    if main_event is None:
        dt = datetime(monday.year, monday.month, monday.day, 12, 0, 0)
        jd_ut = to_jd_ut(dt)
        sun_pos = get_planet_position(jd_ut, swe.SUN)
        moon_pos = get_planet_position(jd_ut, swe.MOON)
        angle = (moon_pos["longitude"] - sun_pos["longitude"]) % 360
        
        if angle < 90:
            phase_name = "Luna Creciente"
        elif angle < 180:
            phase_name = "Luna Gibosa Creciente"
        elif angle < 270:
            phase_name = "Luna Gibosa Menguante"
        else:
            phase_name = "Luna Menguante"
        
        main_event = {
            "main_event": phase_name,
            "date": monday.strftime("%Y-%m-%d"),
            "sign": moon_pos["sign"],
            "is_highlight": False
        }
    
    return main_event


def detect_sign_changes(monday: date, sunday: date) -> list:
    """
    Detecta cambios de signo de Mercurio, Venus y Marte durante la semana.
    """
    sign_changes = []
    
    for planet_name in FAST_PLANETS:
        planet_id = PLANETS[planet_name]
        
        # Posición al inicio de la semana
        dt_start = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
        jd_start = to_jd_ut(dt_start)
        start_pos = get_planet_position(jd_start, planet_id)
        
        prev_sign = start_pos["sign_index"]
        
        # Revisar cada día
        current = monday + timedelta(days=1)
        while current <= sunday:
            dt = datetime(current.year, current.month, current.day, 12, 0, 0)
            jd_ut = to_jd_ut(dt)
            pos = get_planet_position(jd_ut, planet_id)
            
            if pos["sign_index"] != prev_sign:
                sign_changes.append({
                    "planet": planet_name,
                    "planet_es": PLANET_NAMES_ES[planet_name],
                    "from_sign": SIGNS_ES[prev_sign],
                    "to_sign": pos["sign"],
                    "date": current.strftime("%Y-%m-%d")
                })
                prev_sign = pos["sign_index"]
            
            current += timedelta(days=1)
    
    return sign_changes


def detect_retrograde_changes(monday: date, sunday: date) -> list:
    """
    Detecta cambios de dirección (retro/directo) de planetas durante la semana.
    """
    retrograde_changes = []
    planets_to_check = FAST_PLANETS + OUTER_PLANETS + HEAVY_PLANETS
    
    for planet_name in planets_to_check:
        if planet_name == "sun":
            continue
        
        planet_id = PLANETS[planet_name]
        
        # Posición al inicio de la semana
        dt_start = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
        jd_start = to_jd_ut(dt_start)
        start_pos = get_planet_position(jd_start, planet_id)
        
        was_retro = start_pos["retrograde"]
        
        # Revisar cada día
        current = monday + timedelta(days=1)
        while current <= sunday:
            dt = datetime(current.year, current.month, current.day, 12, 0, 0)
            jd_ut = to_jd_ut(dt)
            pos = get_planet_position(jd_ut, planet_id)
            
            if pos["retrograde"] != was_retro:
                retrograde_changes.append({
                    "planet": planet_name,
                    "planet_es": PLANET_NAMES_ES[planet_name],
                    "change": "retrograde" if pos["retrograde"] else "direct",
                    "date": current.strftime("%Y-%m-%d"),
                    "sign": pos["sign"]
                })
                was_retro = pos["retrograde"]
            
            current += timedelta(days=1)
    
    return retrograde_changes


def angular_distance(lon1: float, lon2: float) -> float:
    """Calcula distancia angular entre dos longitudes (0-180°)"""
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff
    return diff


def get_major_aspects(monday: date, sunday: date) -> list:
    """
    Encuentra los aspectos fuertes de la semana, priorizando:
    1. Aspectos entre planetas rápidos (Mercury/Venus/Mars)
    2. Aspectos de rápidos con Saturn/Pluto (solo si orb < 3°)
    3. Jupiter/Uranus/Neptune solo si exacto (orb < 1°)
    
    Retorna máximo 4 aspectos ordenados por prioridad.
    """
    all_aspects = []
    
    # Analizar a mitad de semana para aspectos
    mid_week = monday + timedelta(days=3)
    dt = datetime(mid_week.year, mid_week.month, mid_week.day, 12, 0, 0)
    jd_ut = to_jd_ut(dt)
    
    # Obtener posiciones de todos los planetas
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        if planet_name != "moon":  # Excluir Luna de aspectos semanales
            positions[planet_name] = get_planet_position(jd_ut, planet_id)
    
    planet_list = list(positions.keys())
    
    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            p1, p2 = planet_list[i], planet_list[j]
            
            if p1 == "sun" or p2 == "sun":
                continue
            
            # Skip if any planet failed calculation
            if positions[p1].get("error") or positions[p2].get("error"):
                continue

            lon1 = positions[p1]["longitude"]
            lon2 = positions[p2]["longitude"]
            distance = angular_distance(lon1, lon2)
            
            for asp in ASPECTS:
                diff = abs(distance - asp["angle"])
                
                if diff <= asp["orb"]:
                    # Calcular prioridad
                    priority = 10  # Base baja
                    
                    # Aspectos entre rápidos = alta prioridad
                    if p1 in FAST_PLANETS and p2 in FAST_PLANETS:
                        priority = 1
                    # Rápido con Saturn/Pluto, solo si orb < 3°
                    elif (p1 in FAST_PLANETS and p2 in HEAVY_PLANETS) or \
                         (p2 in FAST_PLANETS and p1 in HEAVY_PLANETS):
                        if diff < 3:
                            priority = 2
                        else:
                            continue  # Saltar si orb > 3°
                    # Outer planets solo si muy exacto
                    elif p1 in OUTER_PLANETS or p2 in OUTER_PLANETS:
                        if diff < 1:
                            priority = 3
                        else:
                            continue  # Saltar si no es exacto
                    else:
                        continue  # Saltar combinaciones no prioritarias
                    
                    # Buscar fecha exacta del aspecto
                    exact_date = find_exact_aspect_date(monday, sunday, p1, p2, asp["angle"])
                    
                    all_aspects.append({
                        "planet_a": p1,
                        "planet_a_es": PLANET_NAMES_ES[p1],
                        "planet_b": p2,
                        "planet_b_es": PLANET_NAMES_ES[p2],
                        "aspect": asp["name"],
                        "aspect_es": asp["name_es"],
                        "exact_date": exact_date,
                        "orb": round(diff, 2),
                        "priority": priority
                    })
    
    # Ordenar por prioridad y retornar máximo 4
    all_aspects.sort(key=lambda x: (x["priority"], x["orb"]))
    return all_aspects[:4]


def find_exact_aspect_date(monday: date, sunday: date, p1: str, p2: str, target_angle: float) -> str:
    """Encuentra la fecha en que el aspecto es más exacto"""
    min_diff = 360
    exact_date = monday
    
    current = monday
    while current <= sunday:
        dt = datetime(current.year, current.month, current.day, 12, 0, 0)
        jd_ut = to_jd_ut(dt)
        
        pos1 = get_planet_position(jd_ut, PLANETS[p1])
        pos2 = get_planet_position(jd_ut, PLANETS[p2])
        
        distance = angular_distance(pos1["longitude"], pos2["longitude"])
        diff = abs(distance - target_angle)
        
        if diff < min_diff:
            min_diff = diff
            exact_date = current
        
        current += timedelta(days=1)
    
    return exact_date.strftime("%Y-%m-%d")


def get_planets_positions(monday: date) -> dict:
    """
    Retorna las posiciones de TODOS los cuerpos celestes al inicio de la semana.
    Incluye: Sol, Luna, planetas, asteroides principales y Lilith.
    """
    dt = datetime(monday.year, monday.month, monday.day, 12, 0, 0)
    jd_ut = to_jd_ut(dt)
    
    result = {
        "planets": {},
        "asteroids": {},
        "lilith": {}
    }
    
    # TODOS los planetas (incluido Sol y Luna)
    for planet_name, planet_id in PLANETS.items():
        pos = get_planet_position(jd_ut, planet_id)
        result["planets"][planet_name] = {
            "planet_es": PLANET_NAMES_ES[planet_name],
            "sign": pos["sign"],
            "degree": round(pos["degree"], 1),
            "retrograde": pos["retrograde"]
        }
    
    # Asteroides
    for asteroid_name, asteroid_id in ASTEROIDS.items():
        pos = get_planet_position(jd_ut, asteroid_id)
        result["asteroids"][asteroid_name] = {
            "asteroid_es": ASTEROID_NAMES_ES[asteroid_name],
            "sign": pos["sign"],
            "degree": round(pos["degree"], 1),
            "retrograde": pos["retrograde"]
        }
    
    # Lilith (Luna Negra)
    for lilith_name, lilith_id in LILITH.items():
        pos = get_planet_position(jd_ut, lilith_id)
        result["lilith"][lilith_name] = {
            "lilith_es": LILITH_NAMES_ES[lilith_name],
            "sign": pos["sign"],
            "degree": round(pos["degree"], 1),
            "retrograde": pos["retrograde"]
        }
    
    return result


def detect_moon_sign_changes(monday: date, sunday: date) -> list:
    """
    Detecta los cambios de signo de la Luna durante la semana (Moon Ingresses).
    Revisa hora por hora para mayor precisión.
    """
    moon_changes = []
    
    # Inicio a las 00:00 del lunes
    current_dt = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
    
    # Fin a las 23:59 del domingo
    end_dt = datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59)
    
    # Obtener estado inicial
    jd_ut = to_jd_ut(current_dt)
    start_pos = get_planet_position(jd_ut, swe.MOON)
    
    # Si hubo error en cálculo inicial, abortar
    if start_pos.get("error"):
        return []
        
    prev_sign_index = start_pos["sign_index"]
    
    # Iterar cada hora
    while current_dt <= end_dt:
        # Avanzar 1 hora
        next_dt = current_dt + timedelta(hours=1)
        if next_dt > end_dt:
            break
            
        jd_ut = to_jd_ut(next_dt)
        pos = get_planet_position(jd_ut, swe.MOON)
        
        if pos.get("error"):
            current_dt = next_dt
            continue
            
        current_sign_index = pos["sign_index"]
        
        if current_sign_index != prev_sign_index:
            # Hubo cambio de signo
            moon_changes.append({
                "date": next_dt.strftime("%Y-%m-%d"),
                "time": next_dt.strftime("%H:%M"),
                "datetime": next_dt.strftime("%Y-%m-%d %H:%M"),
                "entering_sign": pos["sign"],
                "entering_sign_es": pos["sign"], # Redundante pero consistente con otros formatos
                "degree": 0.0, # Al ingresar siempre es 0
                "from_sign": SIGNS_ES[prev_sign_index]
            })
            prev_sign_index = current_sign_index
        
        current_dt = next_dt
            
    return moon_changes


def calculate_weekly_climate(start_date: date = None) -> dict:
    """
    Función principal que calcula todos los datos del clima astral semanal.
    
    Args:
        start_date: Fecha de inicio (cualquier día de la semana deseada)
    
    Returns:
        dict con toda la información para el clima semanal
    """
    monday, sunday = get_week_dates(start_date)
    
    # Debug info
    print(f"DEBUG: Computing weekly climate for week {monday} to {sunday}")

    return {
        "week": {
            "start": monday.strftime("%Y-%m-%d"),
            "end": sunday.strftime("%Y-%m-%d")
        },
        "lunar_phase": get_lunar_phase_events(monday, sunday),
        "moon_sign_changes": detect_moon_sign_changes(monday, sunday),
        "sign_changes": detect_sign_changes(monday, sunday),
        "retrograde_changes": detect_retrograde_changes(monday, sunday),
        "major_aspects": get_major_aspects(monday, sunday),
        "planets_positions": get_planets_positions(monday)
    }
