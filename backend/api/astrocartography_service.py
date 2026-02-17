
import swisseph as swe
from datetime import datetime
from pathlib import Path
import os
from .services import to_jdut1, PLANETS, PLANET_NAMES_ES, fmt_zodiac

# Configuración de path (reutilizada de services.py o settings)
ephe_path = os.environ.get("SE_EPHE_PATH")
if not ephe_path:
    BASE_DIR = Path(__file__).resolve().parents[1]
    ephe_path = str(BASE_DIR.parent / "se_data")

swe.set_ephe_path(ephe_path)

# Constantes para orbes y ángulos
ANGLES = {
    "Asc": {"angle": 270.0, "type": "Horizon"}, # Swiss Azimuth: E=270, W=90, S=0, N=180
    "Desc": {"angle": 90.0, "type": "Horizon"},
    "MC": {"angle": 0.0, "type": "Meridian"},   # Culminación Superior (Sur en HN, Norte en HS - Azimuth 0)
    "IC": {"angle": 180.0, "type": "Meridian"}, # Culminación Inferior
}

# Orbes configurables (en grados)
ORB_ANGULARITY = 10.0 # Para considerar un planeta "Angular"
ORB_PARAN = 2.0       # Orbe de latitud para Parans (estricto)

def calculate_mundane_angularity(jd_ut, lat, lon):
    """
    Calcula planetas angulares (Mundanos) para una ubicación específica.
    """
    swe.set_topo(lon, lat, 0)
    
    # Calcular ARMC y Casas para contexto (opcional para visual debug)
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_TOPOCTR)
    armc = ascmc[2]
    mc_zod = ascmc[1]
    asc_zod = ascmc[0]

    angular_planets = []

    for name, pid in PLANETS.items():
        # 1. Coordenadas Ecuatoriales Topocéntricas (RA, Decl)
        # Necesarias para Azimuth y Altitud precisos
        r_eq = swe.calc_ut(jd_ut, pid, swe.FLG_SWIEPH | swe.FLG_TOPOCTR | swe.FLG_EQUATORIAL)
        ra = r_eq[0][0]
        decl = r_eq[0][1]
        
        # 2. Calcular Azimuth y Altitud
        # geopos: (lon, lat, height)
        geopos = (lon, lat, 0)
        # swe.azalt(tjd, calc_flag, geopos, atpress, attemp, xin)
        # xin: (ra, decl, dist) because FLAG is EQU2HOR
        az_res = swe.azalt(jd_ut, swe.EQU2HOR, geopos, 0, 10, (ra, decl, 1.0))
        
        azimuth = az_res[0]
        altitude = az_res[1]
        
        # 3. Calcular Ángulo Horario (Hour Angle) para MC/IC
        # HA = RAMC - RA (o RA - RAMC dependiento de convención, usamos dist al meridiano)
        # Meridian Distance
        ha = (armc - ra) % 360.0 # Positivo al Oeste
        if ha > 180: ha -= 360  # Rango -180 a +180

        # Chequear Angularidad
        is_angular = False
        angle_found = None
        orb_found = None
        
        # A) Eje Horizonte (Asc/Desc) - Definido por Altitud ~ 0
        if abs(altitude) <= ORB_ANGULARITY:
            # Determinar si es Asc (Este) o Desc (Oeste)
            # Azimuth Swiss: 0=S, 90=W, 180=N, 270=E
            # Asc es naciente (Este), Desc es poniente (Oeste)
            # Rango Asc: Az > 180 (aprox)
            # Rango Desc: Az < 180 (aprox)
            if 180 < azimuth < 360:
                angle_found = "Asc"
            else:
                angle_found = "Desc"
            is_angular = True
            orb_found = altitude # Positivo = Sobre horizonte, Negativo = Bajo horizonte
            
        # B) Eje Meridiano (MC/IC) - Definido por Hour Angle ~ 0 (MC) o ~ 180 (IC)
        # Prioridad a Meridian si es fuerte? O reportar ambos si cruza (raro, solo en polos)
        elif abs(ha) <= ORB_ANGULARITY:
            angle_found = "MC"
            is_angular = True
            orb_found = ha
        elif abs(abs(ha) - 180) <= ORB_ANGULARITY:
            angle_found = "IC"
            is_angular = True
            orb_found = abs(ha) - 180

        if is_angular:
            angular_planets.append({
                "planet": name,
                "planet_name": PLANET_NAMES_ES.get(name, name),
                "angle": angle_found,
                "orb": round(orb_found, 4),
                "altitude": round(altitude, 4),
                "azimuth": round(azimuth, 4),
                "type": "Mundane"
            })
            
    return angular_planets

def calculate_zodiacal_angularity(jd_ut, lat, lon):
    """
    Calcula planetas angulares (Zodiacales) comparando longitud eclíptica con Asc/MC.
    """
    swe.set_topo(lon, lat, 0)
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_TOPOCTR)
    asc_deg = ascmc[0]
    mc_deg = ascmc[1]
    desc_deg = (asc_deg + 180) % 360
    ic_deg = (mc_deg + 180) % 360
    
    angles_zod = {
        "Asc": asc_deg,
        "MC": mc_deg,
        "Desc": desc_deg,
        "IC": ic_deg
    }
    
    angular_planets = []
    
    for name, pid in PLANETS.items():
        # Calcular longitud eclíptica (Topocéntrica para consistencia local)
        res = swe.calc_ut(jd_ut, pid, swe.FLG_SWIEPH | swe.FLG_TOPOCTR)
        p_lon = res[0][0]
        
        for ang_name, ang_deg in angles_zod.items():
            # Distancia mínima circular
            diff = abs(p_lon - ang_deg)
            if diff > 180: diff = 360 - diff
            
            if diff <= ORB_ANGULARITY:
                angular_planets.append({
                    "planet": name,
                    "planet_name": PLANET_NAMES_ES.get(name, name),
                    "angle": ang_name,
                    "orb": round(diff, 4),
                    "zodiac_pos": round(p_lon, 4),
                    "angle_pos": round(ang_deg, 4),
                    "type": "Zodiacal"
                })
                
    return angular_planets

def calculate_parans(jd_ut, lat):
    """
    Identifica Parans (cruces de latitud) activos para la latitud dada.
    (Simplificado: Determina si la latitud actual permite cruces planetarios en ángulos)
    
    Nota: Un "Paran" estricto es una latitud donde dos planetas cruzan ángulos simultáneamente
    a lo largo del día rotacional.
    
    Aquí, verificamos si la latitud dada está cerca de la latitud de un Paran para el par de planetas.
    Esta es una operación compleja.
    
    Alternativa simple solicitada: "Includes Parans (latitude crossings)"
    Si el usuario pide esto, puede referirse a listar qué parans LATITUDE LINES pasan cerca.
    
    Algoritmo:
    Para cada par de planetas (A, B) y par de ángulos (Ang1, Ang2):
      Si existe un tiempo t donde A en Ang1 y B en Ang2:
         La latitud geográfica donde esto ocurre es Lat_Paran.
    
    Esto es costoso de calcular en tiempo real para todos los pares.
    
    Aproximación para MVP: Devolver lista vacía o implementar solo si se conoce la fórmula directa.
    Formula (approx for squaring angles): 
    Parans occur when planets have specific relationship in RA/Decl depending on Lat.
    
    Vamos a dejarlo como placeholder documentado o implementar una lógica básica si es posible.
    Por ahora, retornaremos una lista vacía para no bloquear, explicando la complejidad.
    """
    return []

def process_astrocartography_mundane(payload):
    """
    Procesa la solicitud de Astrocartografía Mundana.
    Payload:
      datetime, lat, lng (Nacimiento del usuario - para JD base)
      targets: [{name, lat, lng}]
    """
    dt_str = payload.get("datetime")
    lat_birth = payload.get("lat") # No se usa realmente para ACG relocada, se usa el tiempo absoluto
    lng_birth = payload.get("lng")
    
    # 1. Obtener JD UT universal (Time invariante)
    # Suponemos que el input datetime es UTC o tiene offset?
    # El standard de la API ha sido ISO string. Asumimos UTC si no hay info, o parseamos.
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            # Asumir UTC si no viene zona, para consistencia global
            from dateutil import tz
            dt = dt.replace(tzinfo=tz.UTC)
    except Exception as e:
        raise ValueError(f"Invalid datetime format: {e}")

    jd_ut = to_jdut1(dt, "UTC") # Usamos nuestra utility, que maneja timezone objects

    results = []
    
    targets = payload.get("targets", [])
    for city in targets:
        c_lat = city.get("lat")
        c_lng = city.get("lng")
        c_name = city.get("name", "Unknown")
        
        # A. Mundane Angularity
        mundane = calculate_mundane_angularity(jd_ut, c_lat, c_lng)
        
        # B. Zodiacal Angularity
        zodiacal = calculate_zodiacal_angularity(jd_ut, c_lat, c_lng)
        
        # C. Parans (Future implementation or simple check)
        parans = calculate_parans(jd_ut, c_lat)
        
        # Filter: Combine meaningful results?
        # User wants simple list.
        
        results.append({
            "city": c_name,
            "lat": c_lat,
            "lng": c_lng,
            "mundane_angles": mundane,
            "zodiacal_angles": zodiacal,
            "parans": parans
        })
        
    return {
        "jd_ut": jd_ut,
        "results": results
    }
