import math, os
import swisseph as swe
from datetime import datetime
import pytz
import pytest

# --- Helpers
def jd_ut_from_local(dt_local_str, tzname):
    tz = pytz.timezone(tzname)
    dt_local = tz.localize(datetime.fromisoformat(dt_local_str))
    dt_utc = dt_local.astimezone(pytz.UTC)
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)

def delta_deg(a, b):
    d = (a - b) % 360.0
    if d > 180: d -= 360
    return abs(d)

# --- Setup Swiss
@pytest.fixture(scope="session", autouse=True)
def setup_swiss():
    ephe_path = os.environ.get("SE_EPHE_PATH", os.path.join(os.path.dirname(__file__), "../../se_data"))
    swe.set_ephe_path(ephe_path)

# --- Snapshots (valores esperados tomados de Astro.com)
cases = [
    {
      "name": "Persona1",
      "dt": "1997-11-06T14:05:00", "tz":"Europe/Madrid",
      "lat": 41.5629623, "lon": 2.0100492,
      "expect": {
        "MOON": 296.9106,   # Capricornio 26° 54' 38" -> 270 + 26.9106 = 296.9106
        "ASC":  317.0833,   # Acuario 17° 05' -> 300 + 17.0833
        "MC":   245.3000    # Sagitario 5° 18' -> 240 + 5.3
      },
      "topo_moon": True
    },
    # Añade tus otras 3 personas con sus longitudes absolutas (0..360)
]

TOL = 0.1  # grados

def test_snapshots():
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    for C in cases:
        jd_ut = jd_ut_from_local(C["dt"], C["tz"])

        # Topo sólo Luna si se pide
        if C.get("topo_moon"):
            swe.set_topo(C["lon"], C["lat"], 0.0)
        else:
            swe.set_topo(0.0, 0.0, 0.0)

        # Luna
        lon_moon, *_ = swe.calc_ut(jd_ut, swe.MOON, flags)
        assert delta_deg(lon_moon, C["expect"]["MOON"]) <= TOL, f"MOON off {delta_deg(lon_moon, C['expect']['MOON']):.3f}°"

        # Volver a geocéntrico para casas/asc/mc si hiciste set_topo
        swe.set_topo(0.0, 0.0, 0.0)

        # Casas, ASC/MC (Placidus)
        cusps, ascmc = swe.houses_ex(jd_ut, flags, C["lat"], C["lon"], b'P')
        asc, mc = ascmc[0], ascmc[1]
        assert delta_deg(asc, C["expect"]["ASC"]) <= TOL, f"ASC off {delta_deg(asc, C['expect']['ASC']):.3f}°"
        assert delta_deg(mc, C["expect"]["MC"])  <= TOL, f"MC off  {delta_deg(mc,  C['expect']['MC']):.3f}°"