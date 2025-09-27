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

# Inicialización Swiss Ephemeris (DE431)
BASE_DIR = Path(__file__).resolve().parents[1]
swe.set_ephe_path(str(BASE_DIR / "se_data"))  # carpeta con sepl*.se1, semo*.se1
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
    Devuelve longitudes eclípticas aparentes (tropical) de planetas.
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
        # Nota: TRUE_NODE es el nodo “verdadero”; para “medio”, usa MEAN_NODE
        lonlat, ret = swe.calc_ut(jdut1, pid, flags)
        lon_ecl = lonlat[0] % 360.0
        results[name] = {
            "value": lon_ecl,
            "formatted": fmt_zodiac(lon_ecl),
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
        "asc": {"value": asc, "formatted": fmt_zodiac(asc)},
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
                        "a": a, "b": b,
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
        planets_geo["moon"] = {"value": moon_topo, "formatted": fmt_zodiac(moon_topo)}

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