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
from datetime import datetime
from dateutil import tz
from pathlib import Path
import os

# Configuración robusta de path de efemérides
# 1. Intentar variable de entorno (Docker/Koyeb)
ephe_path = os.environ.get("SE_EPHE_PATH")

# 2. Fallback: cálculo relativo (Local dev)
if not ephe_path:
    BASE_DIR = Path(__file__).resolve().parents[1]
    ephe_path = str(BASE_DIR.parent / "se_data")

swe.set_ephe_path(ephe_path)  # carpeta con sepl*.se1, semo*.se1
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED        # sin TRUEPOS, sin TOPOCTR

# Planetas que calculemos (Swiss IDs)
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
    "chiron": swe.CHIRON,
    "true_node": swe.TRUE_NODE,
    "lilith": swe.MEAN_APOG,  # Luna Negra Media (Lilith)
}

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

HOUSE_SYSTEMS = {
    "placidus": b'P',
    "equal":    b'E',
    "koch":     b'K',
    "whole":    b'W',
}

# Flags para posiciones aparentes geocéntricas con Swiss
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED  # sin TRUEPOS, sin TOPOCTR

# Aspectos con orbes fijos
ASPECTS = [
    {"name": "Conjunction", "angle": 0,   "orb": 8},
    {"name": "Opposition",  "angle": 180, "orb": 8},
    {"name": "Trine",       "angle": 120, "orb": 7},
    {"name": "Square",      "angle": 90,  "orb": 6},
    {"name": "Sextile",     "angle": 60,  "orb": 4},
    {"name": "Quincunx",    "angle": 150, "orb": 3},
]

def set_ephe_path(ephe_path: str):
    swe.set_ephe_path(ephe_path)

def to_jdut1(datetime_local: datetime, tz_name: str) -> float:
    """
    Convierte una fecha/hora local + zona horaria a Julian Day UT.
    Usa las funciones de Swiss para conversión precisa.
    """
    zone = tz.gettz(tz_name)
    if zone is None:
        raise ValueError(f"Unknown timezone: {tz_name}")
    dt_local = datetime_local.replace(tzinfo=zone)
    dt_utc = dt_local.astimezone(tz.UTC)
    # Usa swe.utc_to_jd para conversión precisa
    iy, im, id = dt_utc.year, dt_utc.month, dt_utc.day
    ih, imin = dt_utc.hour, dt_utc.minute
    sec = dt_utc.second + dt_utc.microsecond / 1e6
    jd_et, jd_ut = swe.utc_to_jd(iy, im, id, ih, imin, sec, swe.GREG_CAL)
    return jd_ut

def fmt_zodiac(lon):
    signs = ["Aries","Tauro","Géminis","Cáncer","Leo","Virgo",
             "Libra","Escorpio","Sagitario","Capricornio","Acuario","Piscis"]
    sign = int(lon // 30) % 12
    deg = lon % 30
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(round((((deg - d) * 60) - m) * 60))
    return f"{signs[sign]} {d}° {m}' {s}\""

def compute_planets(jdut1: float, lat: float, lon: float, topo: bool) -> dict:
    """
    Devuelve longitudes eclípticas aparentes (tropical) de planetas con info de retrógrado.
    """
    results = {}
    flags = FLAGS

    if topo:
        # Topocéntrico para todos (o solo Luna si prefieres)
        swe.set_topo(lon, lat, 0)  # alt=0m (puedes exponerlo en la API)
        flags = flags | swe.FLG_TOPOCTR
    else:
        # geocéntrico
        swe.set_topo(0, 0, 0)

    for name, pid in PLANETS.items():
        # Nota: TRUE_NODE es el nodo "verdadero"; para "medio", usa MEAN_NODE
        lonlat, ret = swe.calc_ut(jdut1, pid, flags)
        lon_ecl = lonlat[0] % 360.0
        speed = lonlat[3]  # velocidad diaria en longitud
        is_retrograde = speed < 0
        
        formatted = fmt_zodiac(lon_ecl)
        if is_retrograde:
            formatted += " ℞"
        
        results[name] = {
            "value": lon_ecl,
            "speed": speed,
            "retrograde": is_retrograde,
            "formatted": formatted,
        }
    return results

def compute_houses(jdut1: float, lat: float, lon: float, house_system: bytes):
    """
    Casas y puntos (Asc, MC) según Swiss (usa UT).
    lon positivo Este (convención Swiss: Este = +).
    """
    # swe.houses_ex(jdut1, lat, lon_east_positive, b'P')
    cusps, ascmc = swe.houses_ex(jdut1, lat, lon, house_system, 0)
    # ascmc indices: 0=Asc, 1=MC, 2=ARMC, 3=Vertex, 4=Equatorial Asc, 5=Co-Asc 1, 6=Co-Asc 2, 7=Polar Asc
    asc = ascmc[0] % 360.0
    mc  = ascmc[1] % 360.0
    houses = [(c % 360.0) for c in cusps]  # 12
    return {
        "ascendente": {"value": asc, "formatted": fmt_zodiac(asc)},
        "asc": {"value": asc, "formatted": fmt_zodiac(asc)},  # alias
        "mc":  {"value": mc,  "formatted": fmt_zodiac(mc)},
        "cusps": [{"house": i+1, "value": h, "formatted": fmt_zodiac(h)} for i, h in enumerate(houses)],
    }

def _norm360(x): 
    y = x % 360.0
    return y if y >= 0 else y + 360.0

def angular_sep(a, b):
    d = abs(_norm360(a) - _norm360(b))
    return min(d, 360.0 - d)

def compute_aspects(planets):
    """Cálculo de aspectos con orbes fijos."""
    names = list(planets.keys())
    out = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            la, lb = planets[a]["value"], planets[b]["value"]
            sep = angular_sep(la, lb)
            for asp in ASPECTS:
                diff = abs(sep - asp["angle"])
                if diff <= asp["orb"]:
                    out.append({
                        "planet_a": a,
                        "planet_b": b,
                        "aspect": asp["name"],
                        "angle": round(sep, 4),
                        "orb": round(diff, 4),
                    })
    return out

def compute_chart(payload: dict, ephe_path: str) -> dict:
    """
    payload esperado:
      {
        "datetime": "1997-11-06T14:05:00",
        "timezone": "Europe/Madrid",
        "latitude": 41.5629623,
        "longitude": 2.0100492,    # Este positivo
        "house_system": "placidus", # o "equal", etc.
        "topocentric_moon_only": true
      }
    """
    set_ephe_path(ephe_path)

    dt = datetime.fromisoformat(payload["datetime"])
    tzname = payload.get("timezone", "UTC")
    lat = float(payload["latitude"])
    lon = float(payload["longitude"])  # Swiss espera Este positivo

    jdut1 = to_jdut1(dt, tzname)

    hs_code = HOUSE_SYSTEMS.get(payload.get("house_system", "placidus"), b'P')

    topo_moon_only = payload.get("topocentric_moon_only", True)

    # 1) Planetas: geocéntricos aparentes
    planets_geo = compute_planets(jdut1, lat, lon, topo=False)

    # 2) Luna topocéntrica (si se pide)
    if topo_moon_only:
        swe.set_topo(lon, lat, 0)
        lonlat, ret = swe.calc_ut(jdut1, swe.MOON, FLAGS | swe.FLG_TOPOCTR)
        moon_topo = lonlat[0] % 360.0
        moon_speed = lonlat[3]
        planets_geo["moon"] = {
            "value": moon_topo,
            "speed": moon_speed,
            "retrograde": moon_speed < 0,
            "formatted": fmt_zodiac(moon_topo) + (" ℞" if moon_speed < 0 else "")
        }

    # 3) Casas (Asc/MC exactos a Swiss)
    houses = compute_houses(jdut1, lat, lon, hs_code)

    # 4) Aspectos
    aspects = compute_aspects(planets_geo)

    return {
        "jd_ut": jdut1,
        "planets": planets_geo,
        "houses": houses,
        "aspects": aspects,
        "meta": {
            "ephe_path": ephe_path,
            "flags": int(FLAGS),
            "house_system": payload.get("house_system", "placidus"),
        }
    }


def get_important_transits(month, year):
    """Calcula tránsitos importantes del mes enfocados en la Luna: aspectos lunares y eclipses solares/lunares"""
    from datetime import datetime, timedelta
    
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    
    transits = []
    current = start_date
    while current < end_date:
        jd = swe.julday(current.year, current.month, current.day)
        positions = {}
        for name, pid in PLANETS.items():
            if name in ["lilith", "chiron"]:  # Excluir lilith y chiron, pero incluir true_node para eclipses
                continue
            result = swe.calc_ut(jd, pid, FLAGS)
            lon = result[0][0]
            positions[name] = lon % 360
        
        # Calcular posición del nodo para eclipses
        node_result = swe.calc_ut(jd, swe.TRUE_NODE, FLAGS)
        node_lon = node_result[0][0] % 360
        
        # Verificar aspectos entre planetas
        planet_list = list(positions.keys())
        for i in range(len(planet_list)):
            for j in range(i+1, len(planet_list)):
                p1, p2 = planet_list[i], planet_list[j]
                diff = abs(positions[p1] - positions[p2]) % 360
                if diff > 180:
                    diff = 360 - diff
                
                aspect = None
                if diff < 10:
                    aspect = "Conjunción"
                elif abs(diff - 60) < 10:
                    aspect = "Sextil"
                elif abs(diff - 90) < 10:
                    aspect = "Cuadratura"
                elif abs(diff - 120) < 10:
                    aspect = "Trígono"
                elif abs(diff - 180) < 10:
                    aspect = "Oposición"
                
                if aspect:
                    # Verificar si es eclipse
                    is_eclipse = False
                    if {p1, p2} == {"sun", "moon"}:
                        moon_lon = positions["moon"]
                        # Eclipse Solar: Luna Nueva (conjunción) dentro de 15° del Nodo Lunar
                        if aspect == "Conjunción" and min(abs(moon_lon - node_lon), 360 - abs(moon_lon - node_lon)) < 15:
                            aspect = "Eclipse Solar"
                            is_eclipse = True
                        # Eclipse Lunar: Luna Llena (oposición) dentro de 12-15° del Nodo Lunar opuesto
                        elif aspect == "Oposición" and min(abs(moon_lon - (node_lon + 180) % 360), 360 - abs(moon_lon - (node_lon + 180) % 360)) < 15:
                            aspect = "Eclipse Lunar"
                            is_eclipse = True
                    
                    transits.append({
                        "date": current.strftime("%Y-%m-%d"),
                        "aspect": aspect,
                        "planets": [PLANET_NAMES_ES.get(p1, p1), PLANET_NAMES_ES.get(p2, p2)],
                        "angle": round(diff, 2),
                        "is_eclipse": is_eclipse
                    })
        
        current += timedelta(days=1)
    
    # Filtrar solo tránsitos lunares (que involucran a la Luna) y eclipses
    lunar_transits = [t for t in transits if "Luna" in t["planets"]]
    
    # Eliminar duplicados aproximados (mismo aspecto en días consecutivos)
    unique_transits = []
    seen = set()
    for t in lunar_transits:
        key = (t["aspect"], tuple(sorted(t["planets"])), t["date"][:7])  # mes-año
        if key not in seen:
            unique_transits.append(t)
            seen.add(key)
    
    return unique_transits

def get_lunar_phase(sun_lon: float, moon_lon: float) -> str:
    """Calcula la fase lunar basada en la separación angular Sol-Luna"""
    angle = (moon_lon - sun_lon) % 360
    
    if angle < 45:
        return "Luna Nueva"
    elif angle < 90:
        return "Creciente Menguante"  # Waxing Crescent
    elif angle < 135:
        return "Cuarto Creciente"  # First Quarter
    elif angle < 180:
        return "Creciente Gibosa"  # Waxing Gibbous
    elif angle < 225:
        return "Luna Llena"
    elif angle < 270:
        return "Menguante Gibosa"  # Waning Gibbous
    elif angle < 315:
        return "Cuarto Menguante"  # Last Quarter
    else:
        return "Menguante Creciente"  # Waning Crescent

def calculate_eclipses(year: int):
    """
    Calcula todos los eclipses (solares y lunares) para un año dado.
    Retorna detalles incluyendo signo, grado y nodo asociado.
    """
    from datetime import datetime
    
    eclipses = []
    start_time = swe.julday(year, 1, 1)
    end_time = swe.julday(year, 12, 31)
    
    t = start_time
    
    # 1. Buscar Eclipses Solares
    while True:
        # swe.sol_eclipse_when_glob(tjd_start, iflags) -> (retflag, [tret, corel...])
        res = swe.sol_eclipse_when_glob(t, swe.FLG_SWIEPH)
        if res[0] == -1:
            break
        
        t_max = res[1][0]  # Tiempo del máximo eclipse
        if t_max > end_time:
            break
            
        # Detalles del eclipse
        # Convertir a fecha
        year_e, month_e, day_e, hour_e = swe.revjul(t_max)
        dt_eclipse = datetime(year_e, month_e, day_e, int(hour_e), int((hour_e % 1) * 60))
        
        # Calcular posiciones para determinar signo y nodo
        # Sol y Luna están en conjunción cerca del nodo
        pos_sun = swe.calc_ut(t_max, swe.SUN, swe.FLG_SWIEPH)[0][0]
        pos_node = swe.calc_ut(t_max, swe.TRUE_NODE, swe.FLG_SWIEPH)[0][0] # Nodo Norte real
        
        # Signo del eclipse (posición del Sol/Luna)
        sign_eclipse = fmt_zodiac(pos_sun).split(" ")[0]
        
        # Determinar si es Nodo Norte o Sur
        # Si el Sol está cerca del Nodo Norte (dentro de ~20°), es Nodo Norte.
        # Si está opuesto (~180°), es Nodo Sur.
        dist_north = min(abs(pos_sun - pos_node), 360 - abs(pos_sun - pos_node))
        dist_south = min(abs(pos_sun - (pos_node + 180) % 360), 360 - abs(pos_sun - (pos_node + 180) % 360))
        
        node_name = "Nodo Norte" if dist_north < dist_south else "Nodo Sur"
        
        # Tipo de eclipse solar
        # eclipse_type index 9 in res[1] is not standardized in python wrapper output sometimes, rely on flag or calc?
        # En sol_eclipse_when_glob:
        # bit 0: central, bit 1: non-central, bit 2: total, bit 3: annular, bit 4: partial
        # Simplificación basada en corel (res[1][1] - res[1][8] etc is complex), let's use simpler logic if accessible or basic classification
        # For now, generic "Solar" is safe, refine if flags available easily.
        # Actually retflag contains bits.
        flags = res[0]
        subtype = "Parcial"
        if flags & swe.ECL_TOTAL: subtype = "Total"
        elif flags & swe.ECL_ANNULAR: subtype = "Anular"
        elif flags & swe.ECL_ANNULAR_TOTAL: subtype = "Híbrido"
        
        eclipses.append({
            "date": dt_eclipse.strftime("%Y-%m-%d"),
            "datetime": dt_eclipse.isoformat(),
            "type": "Solar",
            "subtype": subtype,
            "sign": sign_eclipse,
            "degree": round(pos_sun % 30, 2),
            "abs_degree": round(pos_sun, 2),
            "node": node_name,
            "node_sign": fmt_zodiac(pos_node if node_name == "Nodo Norte" else (pos_node + 180) % 360).split(" ")[0],
            "proximity": round(dist_north if node_name == "Nodo Norte" else dist_south, 2)
        })
        
        t = t_max + 20 # avanzar ~20 días para buscar el siguiente
        
    # 2. Buscar Eclipses Lunares
    t = start_time
    while True:
        res = swe.lun_eclipse_when(t, swe.FLG_SWIEPH)
        if res[0] == -1:
            break
            
        t_max = res[1][0]
        if t_max > end_time:
            break
            
        year_e, month_e, day_e, hour_e = swe.revjul(t_max)
        dt_eclipse = datetime(year_e, month_e, day_e, int(hour_e), int((hour_e % 1) * 60))
        
        # En eclipse lunar, Luna opuesta al Sol. Signo del eclipse = Signo de la Luna.
        pos_moon = swe.calc_ut(t_max, swe.MOON, swe.FLG_SWIEPH)[0][0]
        pos_node = swe.calc_ut(t_max, swe.TRUE_NODE, swe.FLG_SWIEPH)[0][0]
        
        sign_eclipse = fmt_zodiac(pos_moon).split(" ")[0]
        
        # Determinar nodo. Luna cerca del nodo -> eclipse.
        dist_north = min(abs(pos_moon - pos_node), 360 - abs(pos_moon - pos_node))
        dist_south = min(abs(pos_moon - (pos_node + 180) % 360), 360 - abs(pos_moon - (pos_node + 180) % 360))
        
        node_name = "Nodo Norte" if dist_north < dist_south else "Nodo Sur"
        
        flags = res[0]
        subtype = "Penumbral" # Default weak
        if flags & swe.ECL_TOTAL: subtype = "Total"
        elif flags & swe.ECL_PARTIAL: subtype = "Parcial"
        
        eclipses.append({
            "date": dt_eclipse.strftime("%Y-%m-%d"),
            "datetime": dt_eclipse.isoformat(),
            "type": "Lunar",
            "subtype": subtype,
            "sign": sign_eclipse,
            "degree": round(pos_moon % 30, 2),
            "abs_degree": round(pos_moon, 2),
            "node": node_name,
            "node_sign": fmt_zodiac(pos_node if node_name == "Nodo Norte" else (pos_node + 180) % 360).split(" ")[0],
            "proximity": round(dist_north if node_name == "Nodo Norte" else dist_south, 2)
        })
        
        t = t_max + 20

    # Ordenar por fecha
    eclipses.sort(key=lambda x: x["datetime"])
    return eclipses


# ==============================================================================
# LÓGICA DEL CLIMA SEMANAL (Movido desde weekly_climate_service.py)
# ==============================================================================
FAST_PLANETS = ["mercury", "venus", "mars"]
HEAVY_PLANETS = ["saturn", "pluto"]
OUTER_PLANETS = ["jupiter", "uranus", "neptune"]

SIGNS_ES = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

ASPECTS = [
    {"name": "conjunction", "name_es": "Conjunción", "angle": 0, "orb": 8},
    {"name": "opposition", "name_es": "Oposición", "angle": 180, "orb": 8},
    {"name": "square", "name_es": "Cuadratura", "angle": 90, "orb": 7},
    {"name": "trine", "name_es": "Trígono", "angle": 120, "orb": 7},
]

def get_lunar_phase_name_and_highlight(angle: float) -> tuple:
    if angle < 1 or angle > 359:
        return "Luna Nueva", True
    elif angle < 89:
        return "Luna Creciente", False
    elif angle < 91:
        return "Cuarto Creciente", False
    elif angle < 179:
        return "Gibosa Creciente", False
    elif angle < 181:
        return "Luna Llena", True
    elif angle < 269:
        return "Gibosa Menguante", False
    elif angle < 271:
        return "Cuarto Menguante", False
    else:
        return "Luna Menguante", False

from datetime import date as dt_date, timedelta as dt_timedelta

def get_week_dates(start_date: dt_date = None) -> tuple:
    if start_date is None:
        start_date = dt_date.today()
    days_since_monday = start_date.weekday()
    monday = start_date - dt_timedelta(days=days_since_monday)
    return monday, monday + dt_timedelta(days=6)

def to_jd_ut_climate(dt: datetime, tzname: str = "UTC") -> float:
    zone = tz.gettz(tzname)
    if zone:
        dt_local = dt.replace(tzinfo=zone)
        dt_utc = dt_local.astimezone(tz.UTC)
    else:
        dt_utc = dt
    jd_et, jd_ut = swe.utc_to_jd(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour, dt_utc.minute, dt_utc.second, swe.GREG_CAL
    )
    return jd_ut

def get_planet_position_climate(jd_ut: float, planet_id: int) -> dict:
    try:
        lonlat, ret = swe.calc_ut(jd_ut, planet_id, FLAGS)
        lon = lonlat[0] % 360.0
        return {
            "longitude": lon, "sign_index": int(lon // 30),
            "sign": SIGNS_ES[int(lon // 30)], "degree": lon % 30,
            "speed": lonlat[3], "retrograde": lonlat[3] < 0, "error": None
        }
    except Exception as e:
        return {"longitude": 0.0, "sign_index": 0, "sign": "Error", "degree": 0.0, "speed": 0.0, "retrograde": False, "error": str(e)}

def find_exact_phase_time(jd_start: float, jd_end: float, target_angle: float) -> tuple:
    TOLERANCE = 0.000694 # ~1 minute
    start = jd_start
    end = jd_end
    for _ in range(25):
        mid = (start + end) / 2
        moon_pos = get_planet_position_climate(mid, swe.MOON)
        sun_pos = get_planet_position_climate(mid, swe.SUN)
        
        angle = (moon_pos["longitude"] - sun_pos["longitude"]) % 360
        diff = (angle - target_angle) % 360
        if diff > 180:
            diff -= 360
            
        if diff < 0:
            start = mid
        else:
            end = mid
            
        if (end - start) < TOLERANCE:
            break
            
    final_jd = (start + end) / 2
    y, m, d, h, mi, s = swe.jdut1_to_utc(final_jd, swe.GREG_CAL)
    dt_exact = datetime(y, m, d, int(h), int(mi), int(s))
    final_pos = get_planet_position_climate(final_jd, swe.MOON)
    return dt_exact, final_pos["sign"]

def get_lunar_phase_events(monday: dt_date, sunday: dt_date) -> dict:
    main_event = None
    current = monday
    dt_prev = datetime(current.year, current.month, current.day, 0, 0, 0)
    jd_ut_prev = to_jd_ut_climate(dt_prev)
    sun_pos_prev = get_planet_position_climate(jd_ut_prev, swe.SUN)
    moon_pos_prev = get_planet_position_climate(jd_ut_prev, swe.MOON)
    angle_prev = (moon_pos_prev["longitude"] - sun_pos_prev["longitude"]) % 360
    quad_prev = int(angle_prev // 90)
    phase_inicio, _ = get_lunar_phase_name_and_highlight(angle_prev)
    
    while current <= sunday:
        current += dt_timedelta(days=1)
        dt_next = datetime(current.year, current.month, current.day, 0, 0, 0)
        jd_ut_next = to_jd_ut_climate(dt_next)
        sun_pos_next = get_planet_position_climate(jd_ut_next, swe.SUN)
        moon_pos_next = get_planet_position_climate(jd_ut_next, swe.MOON)
        angle_next = (moon_pos_next["longitude"] - sun_pos_next["longitude"]) % 360
        quad_next = int(angle_next // 90)
        
        if quad_next != quad_prev and not (quad_prev == 0 and quad_next == 3):
            phase_name = ""
            is_highlight = False
            target_angle = 0
            
            if quad_prev == 3 and quad_next == 0:
                phase_name = "Luna Nueva"
                is_highlight = True
                target_angle = 0
            elif quad_prev == 0 and quad_next == 1:
                phase_name = "Cuarto Creciente"
                target_angle = 90
            elif quad_prev == 1 and quad_next == 2:
                phase_name = "Luna Llena"
                is_highlight = True
                target_angle = 180
            elif quad_prev == 2 and quad_next == 3:
                phase_name = "Cuarto Menguante"
                target_angle = 270
                
            if phase_name:
                jd_prev = to_jd_ut_climate(dt_next - dt_timedelta(days=1))
                exact_dt, exact_sign = find_exact_phase_time(jd_prev, jd_ut_next, target_angle)
                
                event = {
                    "main_event": phase_name,
                    "date": exact_dt.strftime("%Y-%m-%d"),
                    "sign": exact_sign,
                    "is_highlight": is_highlight
                }
                if is_highlight:
                    return event
                elif main_event is None:
                    main_event = event
        quad_prev = quad_next
        
    if main_event is None:
        main_event = {"main_event": phase_inicio, "date": monday.strftime("%Y-%m-%d"), "sign": moon_pos_prev["sign"], "is_highlight": False}
    return main_event

def find_exact_ingress_time(jd_start: float, jd_end: float, planet_id: int, from_sign_index: int) -> tuple:
    TOLERANCE = 0.000694
    start = jd_start
    end = jd_end
    while (end - start) > TOLERANCE:
        mid = (start + end) / 2
        pos = get_planet_position_climate(mid, planet_id)
        if pos["sign_index"] == from_sign_index:
            start = mid
        else:
            end = mid
    final_jd = end
    y, m, d, h, mi, s = swe.jdut1_to_utc(final_jd, swe.GREG_CAL)
    dt_change = datetime(y, m, d, int(h), int(mi), int(s))
    final_pos = get_planet_position_climate(final_jd, planet_id)
    return dt_change, final_pos["sign"]

def detect_sign_changes_climate(monday: dt_date, sunday: dt_date) -> list:
    sign_changes = []
    
    all_bodies = []
    for name, pid in PLANETS.items():
        all_bodies.append((name, PLANET_NAMES_ES.get(name, name.capitalize()), pid))
    
    for name, name_es, planet_id in all_bodies:
        current_dt = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
        current_jd = to_jd_ut_climate(current_dt)
        start_pos = get_planet_position_climate(current_jd, planet_id)
        current_sign_idx = start_pos["sign_index"]
        
        for i in range(1, 8):
            next_dt = current_dt + dt_timedelta(days=i)
            next_jd = to_jd_ut_climate(next_dt)
            next_pos = get_planet_position_climate(next_jd, planet_id)
            if next_pos["sign_index"] != current_sign_idx:
                prev_jd = to_jd_ut_climate(next_dt - dt_timedelta(days=1))
                exact_dt, to_sign_str = find_exact_ingress_time(prev_jd, next_jd, planet_id, current_sign_idx)
                sign_changes.append({
                    "planet": name, "planet_es": name_es or name.capitalize(),
                    "from_sign": SIGNS_ES[current_sign_idx], "to_sign": to_sign_str,
                    "date": exact_dt.strftime("%Y-%m-%d"), "time_utc": exact_dt.strftime("%H:%M"),
                    "datetime_utc": exact_dt.isoformat()
                })
                current_sign_idx = next_pos["sign_index"]
    sign_changes.sort(key=lambda x: x["datetime_utc"])
    return sign_changes

def detect_retrograde_changes_climate(monday: dt_date, sunday: dt_date) -> list:
    retrograde_changes = []
    planets_to_check = FAST_PLANETS + OUTER_PLANETS + HEAVY_PLANETS
    for planet_name in planets_to_check:
        if planet_name == "sun": continue
        planet_id = PLANETS[planet_name]
        dt_start = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
        jd_start = to_jd_ut_climate(dt_start)
        start_pos = get_planet_position_climate(jd_start, planet_id)
        was_retro = start_pos["retrograde"]
        
        current = monday + dt_timedelta(days=1)
        while current <= sunday:
            dt = datetime(current.year, current.month, current.day, 12, 0, 0)
            pos = get_planet_position_climate(to_jd_ut_climate(dt), planet_id)
            if pos["retrograde"] != was_retro:
                retrograde_changes.append({
                    "planet": planet_name, "planet_es": PLANET_NAMES_ES.get(planet_name, planet_name.capitalize()),
                    "change": "retrograde" if pos["retrograde"] else "direct",
                    "date": current.strftime("%Y-%m-%d"), "sign": pos["sign"]
                })
                was_retro = pos["retrograde"]
            current += dt_timedelta(days=1)
    return retrograde_changes

def angular_distance(lon1: float, lon2: float) -> float:
    diff = abs(lon1 - lon2)
    if diff > 180: diff = 360 - diff
    return diff

def find_exact_aspect_date(monday: dt_date, sunday: dt_date, p1: str, p2: str, target_angle: float) -> str:
    min_diff = 360
    exact_date = monday
    current = monday
    while current <= sunday:
        dt = datetime(current.year, current.month, current.day, 12, 0, 0)
        jd_ut = to_jd_ut_climate(dt)
        pos1 = get_planet_position_climate(jd_ut, PLANETS[p1])
        pos2 = get_planet_position_climate(jd_ut, PLANETS[p2])
        diff = abs(angular_distance(pos1["longitude"], pos2["longitude"]) - target_angle)
        if diff < min_diff:
            min_diff = diff
            exact_date = current
        current += dt_timedelta(days=1)
    return exact_date.strftime("%Y-%m-%d")

def get_major_aspects_climate(monday: dt_date, sunday: dt_date) -> list:
    all_aspects = []
    mid_week = monday + dt_timedelta(days=3)
    dt = datetime(mid_week.year, mid_week.month, mid_week.day, 12, 0, 0)
    jd_ut = to_jd_ut_climate(dt)
    
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        if planet_name != "moon":
            positions[planet_name] = get_planet_position_climate(jd_ut, planet_id)
    
    planet_list = list(positions.keys())
    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            p1, p2 = planet_list[i], planet_list[j]
            if p1 == "sun" or p2 == "sun" or positions[p1].get("error") or positions[p2].get("error"):
                continue
            lon1, lon2 = positions[p1]["longitude"], positions[p2]["longitude"]
            distance = angular_distance(lon1, lon2)
            
            for asp in ASPECTS:
                diff = abs(distance - asp["angle"])
                if diff <= asp["orb"]:
                    priority = 10
                    if p1 in FAST_PLANETS and p2 in FAST_PLANETS: priority = 1
                    elif (p1 in FAST_PLANETS and p2 in HEAVY_PLANETS) or (p2 in FAST_PLANETS and p1 in HEAVY_PLANETS):
                        if diff < 3: priority = 2
                        else: continue
                    elif p1 in OUTER_PLANETS or p2 in OUTER_PLANETS:
                        if diff < 1: priority = 3
                        else: continue
                    else: continue
                    
                    exact_date = find_exact_aspect_date(monday, sunday, p1, p2, asp["angle"])
                    all_aspects.append({
                        "planet_a": p1, "planet_a_es": PLANET_NAMES_ES.get(p1, p1.capitalize()),
                        "planet_b": p2, "planet_b_es": PLANET_NAMES_ES.get(p2, p2.capitalize()),
                        "aspect": asp["name"], "aspect_es": asp["name_es"],
                        "exact_date": exact_date, "orb": round(diff, 2), "priority": priority
                    })
    all_aspects.sort(key=lambda x: (x["priority"], x["orb"]))
    return all_aspects[:4]

def get_planets_positions_climate(monday: dt_date) -> dict:
    dt = datetime(monday.year, monday.month, monday.day, 12, 0, 0)
    jd_ut = to_jd_ut_climate(dt)
    result = {"planets": {}, "asteroids": {}, "lilith": {}, "nodes": {}}
    
    REAL_PLANETS = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"}
    
    for pt_name, pt_id in PLANETS.items():
        if pt_name in REAL_PLANETS:
            pos = get_planet_position_climate(jd_ut, pt_id)
            result["planets"][pt_name] = {"planet_es": PLANET_NAMES_ES.get(pt_name, pt_name.capitalize()), "sign": pos["sign"], "degree": round(pos["degree"], 1), "retrograde": pos["retrograde"]}
    
    chiron_pos = get_planet_position_climate(jd_ut, swe.CHIRON)
    result["asteroids"]["chiron"] = {"asteroid_es": "Quirón", "sign": chiron_pos["sign"], "degree": round(chiron_pos["degree"], 1), "retrograde": chiron_pos["retrograde"]}
    
    lilith_pos = get_planet_position_climate(jd_ut, swe.MEAN_APOG)
    result["lilith"]["lilith"] = {"lilith_es": "Lilith", "sign": lilith_pos["sign"], "degree": round(lilith_pos["degree"], 1), "retrograde": lilith_pos["retrograde"]}
    
    nn_pos = get_planet_position_climate(jd_ut, swe.TRUE_NODE)
    result["nodes"]["north_node"] = {"node_es": "Nodo Norte", "sign": nn_pos["sign"], "degree": round(nn_pos["degree"], 1), "retrograde": nn_pos["retrograde"]}
    sn_lon = (nn_pos["longitude"] + 180.0) % 360.0
    
    result["nodes"]["south_node"] = {"node_es": "Nodo Sur", "sign": SIGNS_ES[int(sn_lon // 30)], "degree": round(sn_lon % 30, 1), "retrograde": nn_pos["retrograde"]}
    return result

def detect_moon_sign_changes_climate(monday: dt_date, sunday: dt_date) -> list:
    moon_changes = []
    current_dt = datetime(monday.year, monday.month, monday.day, 0, 0, 0)
    end_dt = datetime(sunday.year, sunday.month, sunday.day, 23, 59, 59)
    jd_ut = to_jd_ut_climate(current_dt)
    start_pos = get_planet_position_climate(jd_ut, swe.MOON)
    if start_pos.get("error"): return []
    prev_sign_index = start_pos["sign_index"]
    
    while current_dt <= end_dt:
        next_dt = current_dt + dt_timedelta(hours=1)
        if next_dt > end_dt: break
        jd_ut = to_jd_ut_climate(next_dt)
        pos = get_planet_position_climate(jd_ut, swe.MOON)
        if pos.get("error"):
            current_dt = next_dt
            continue
        current_sign_index = pos["sign_index"]
        if current_sign_index != prev_sign_index:
            sun_pos = get_planet_position_climate(jd_ut, swe.SUN)
            if sun_pos.get("error"):
                 phase_name = "Desconocida"
            else:
                angle = (pos["longitude"] - sun_pos["longitude"]) % 360
                phase_name, _ = get_lunar_phase_name_and_highlight(angle)
            moon_changes.append({
                "date": next_dt.strftime("%Y-%m-%d"), "time": next_dt.strftime("%H:%M"),
                "datetime": next_dt.strftime("%Y-%m-%d %H:%M"), "entering_sign": pos["sign"],
                "entering_sign_es": pos["sign"], "degree": 0.0, "from_sign": SIGNS_ES[prev_sign_index], "phase": phase_name
            })
            prev_sign_index = current_sign_index
        current_dt = next_dt
    return moon_changes

def calculate_weekly_climate(start_date: dt_date = None) -> dict:
    monday, sunday = get_week_dates(start_date)
    return {
        "week": {"start": monday.strftime("%Y-%m-%d"), "end": sunday.strftime("%Y-%m-%d")},
        "lunar_phase": get_lunar_phase_events(monday, sunday),
        "moon_sign_changes": detect_moon_sign_changes_climate(monday, sunday),
        "sign_changes": detect_sign_changes_climate(monday, sunday),
        "retrograde_changes": detect_retrograde_changes_climate(monday, sunday),
        "major_aspects": get_major_aspects_climate(monday, sunday),
        "planets_positions": get_planets_positions_climate(monday)
    }
