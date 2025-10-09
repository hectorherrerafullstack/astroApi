"""
Ejemplos de uso de la API de Horóscopo Diario
Cliente Python para integración en otras aplicaciones
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

class AstroAPIClient:
    """Cliente para la API de astrología"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def calcular_carta_natal(self, datos_nacimiento: dict) -> dict:
        """
        Calcula la carta natal del usuario (hacer una sola vez).
        
        Args:
            datos_nacimiento: {
                "datetime": "1992-12-07T23:58:00",
                "timezone": "America/Tegucigalpa",
                "latitude": 14.0723,
                "longitude": -87.1921,
                "house_system": "P",
                "topocentric_moon_only": False
            }
        
        Returns:
            dict: Carta natal completa con planetas y casas
        """
        response = self.session.post(
            f"{self.base_url}/compute/",
            json=datos_nacimiento,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def horoscopo_diario(
        self, 
        carta_natal: dict, 
        fecha: Optional[str] = None,
        timezone: str = "UTC"
    ) -> dict:
        """
        Obtiene horóscopo diario personalizado.
        
        Args:
            carta_natal: Resultado de calcular_carta_natal()
            fecha: Formato "YYYY-MM-DD" (None = hoy)
            timezone: Zona horaria (ej: "America/Tegucigalpa")
        
        Returns:
            dict: Horóscopo con aspectos, casas e interpretación
        """
        payload = {
            "birth_data": {
                "planets": carta_natal["planets"],
                "houses": carta_natal["houses"]
            },
            "timezone": timezone
        }
        
        if fecha:
            payload["target_date"] = fecha
        
        response = self.session.post(
            f"{self.base_url}/horoscope/daily/",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def obtener_transitos(
        self, 
        fecha: Optional[str] = None,
        timezone: str = "UTC"
    ) -> dict:
        """
        Obtiene posiciones planetarias (tránsitos) para una fecha.
        
        Args:
            fecha: Formato "YYYY-MM-DD" (None = hoy)
            timezone: Zona horaria
        
        Returns:
            dict: Tránsitos planetarios
        """
        params = {"timezone": timezone}
        if fecha:
            params["date"] = fecha
        
        response = self.session.get(
            f"{self.base_url}/transits/",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()


# =============================================================================
# EJEMPLO 1: Uso básico - Horóscopo del día
# =============================================================================

def ejemplo_basico():
    """Ejemplo simple: calcular horóscopo del día"""
    print("\n" + "="*80)
    print("EJEMPLO 1: Horóscopo del día")
    print("="*80)
    
    client = AstroAPIClient()
    
    # Datos de nacimiento
    datos = {
        "datetime": "1992-12-07T23:58:00",
        "timezone": "America/Tegucigalpa",
        "latitude": 14.0723,
        "longitude": -87.1921,
        "house_system": "P",
        "topocentric_moon_only": False
    }
    
    # 1. Calcular carta natal (hacer UNA VEZ y guardar)
    print("\n1. Calculando carta natal...")
    carta_natal = client.calcular_carta_natal(datos)
    print(f"   ✅ Carta calculada - Ascendente: {carta_natal['houses']['ascendente']['formatted']}")
    
    # 2. Obtener horóscopo del día
    print("\n2. Obteniendo horóscopo del día...")
    horoscopo = client.horoscopo_diario(carta_natal, timezone="America/Tegucigalpa")
    
    print(f"\n📅 Horóscopo para: {horoscopo['date']}")
    print(f"\n⭐ Top 3 Aspectos:")
    for i, asp in enumerate(horoscopo['top_aspects'][:3], 1):
        print(f"   {i}. {asp['transit_planet'].upper()} {asp['aspect']} {asp['natal_planet'].upper()}")
        print(f"      Orbe: {asp['orb']:.2f}° | {'Aplicativo' if asp['applying'] else 'Separativo'}")
    
    print(f"\n💡 Consejo: {horoscopo['interpretation']['advice']}")


# =============================================================================
# EJEMPLO 2: Sistema de caché - Optimización para apps
# =============================================================================

def ejemplo_con_cache():
    """Ejemplo con sistema de caché para optimizar requests"""
    print("\n" + "="*80)
    print("EJEMPLO 2: Sistema con caché (para apps en producción)")
    print("="*80)
    
    import pickle
    from pathlib import Path
    
    client = AstroAPIClient()
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    
    # Definir usuario
    user_id = "user_12345"
    carta_cache = cache_dir / f"{user_id}_natal.pkl"
    
    # Intentar cargar carta natal del caché
    if carta_cache.exists():
        print(f"\n✅ Carta natal encontrada en caché: {carta_cache}")
        with open(carta_cache, "rb") as f:
            carta_natal = pickle.load(f)
    else:
        print("\n⏳ Calculando carta natal (primera vez)...")
        datos = {
            "datetime": "1992-12-07T23:58:00",
            "timezone": "America/Tegucigalpa",
            "latitude": 14.0723,
            "longitude": -87.1921,
            "house_system": "P",
            "topocentric_moon_only": False
        }
        carta_natal = client.calcular_carta_natal(datos)
        
        # Guardar en caché
        with open(carta_cache, "wb") as f:
            pickle.dump(carta_natal, f)
        print(f"✅ Carta guardada en caché: {carta_cache}")
    
    # Obtener horóscopo (esto se hace cada día)
    print("\n⏳ Obteniendo horóscopo del día...")
    horoscopo = client.horoscopo_diario(carta_natal, timezone="America/Tegucigalpa")
    
    print(f"\n📅 {horoscopo['date']}")
    print(f"🏠 Casas activadas: {len(horoscopo['houses_activated'])}")
    print(f"⭐ Aspectos importantes: {len(horoscopo['top_aspects'])}")


# =============================================================================
# EJEMPLO 3: Horóscopo para múltiples usuarios (batch processing)
# =============================================================================

def ejemplo_multiple_usuarios():
    """Ejemplo para procesar horóscopo de múltiples usuarios"""
    print("\n" + "="*80)
    print("EJEMPLO 3: Horóscopo para múltiples usuarios")
    print("="*80)
    
    client = AstroAPIClient()
    
    # Base de datos simulada de usuarios con sus cartas natales
    usuarios = [
        {
            "id": "user_001",
            "nombre": "Juan",
            "datos": {
                "datetime": "1992-12-07T23:58:00",
                "timezone": "America/Tegucigalpa",
                "latitude": 14.0723,
                "longitude": -87.1921,
                "house_system": "P",
                "topocentric_moon_only": False
            }
        },
        {
            "id": "user_002",
            "nombre": "María",
            "datos": {
                "datetime": "1995-03-15T10:30:00",
                "timezone": "America/Mexico_City",
                "latitude": 19.4326,
                "longitude": -99.1332,
                "house_system": "P",
                "topocentric_moon_only": False
            }
        }
    ]
    
    print(f"\n⏳ Procesando horóscopo para {len(usuarios)} usuarios...\n")
    
    resultados = []
    for usuario in usuarios:
        try:
            # Calcular carta natal
            carta = client.calcular_carta_natal(usuario["datos"])
            
            # Obtener horóscopo del día
            horoscopo = client.horoscopo_diario(
                carta, 
                timezone=usuario["datos"]["timezone"]
            )
            
            # Extraer resumen
            resumen = {
                "usuario_id": usuario["id"],
                "nombre": usuario["nombre"],
                "fecha": horoscopo["date"],
                "consejo": horoscopo["interpretation"]["advice"],
                "aspectos_count": len(horoscopo["top_aspects"]),
                "top_aspecto": horoscopo["top_aspects"][0] if horoscopo["top_aspects"] else None
            }
            
            resultados.append(resumen)
            print(f"✅ {usuario['nombre']}: {resumen['aspectos_count']} aspectos detectados")
            
        except Exception as e:
            print(f"❌ Error procesando {usuario['nombre']}: {e}")
    
    # Guardar resultados
    with open("horoscopos_batch.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Resultados guardados en: horoscopos_batch.json")


# =============================================================================
# EJEMPLO 4: Horóscopo semanal (próximos 7 días)
# =============================================================================

def ejemplo_horoscopo_semanal():
    """Genera horóscopo para los próximos 7 días"""
    print("\n" + "="*80)
    print("EJEMPLO 4: Horóscopo Semanal")
    print("="*80)
    
    client = AstroAPIClient()
    
    # Calcular carta natal
    datos = {
        "datetime": "1992-12-07T23:58:00",
        "timezone": "America/Tegucigalpa",
        "latitude": 14.0723,
        "longitude": -87.1921,
        "house_system": "P",
        "topocentric_moon_only": False
    }
    
    print("\n⏳ Calculando carta natal...")
    carta_natal = client.calcular_carta_natal(datos)
    
    print("\n📅 Generando horóscopo para próximos 7 días...\n")
    
    hoy = datetime.now()
    semana = []
    
    for i in range(7):
        fecha = hoy + timedelta(days=i)
        fecha_str = fecha.strftime("%Y-%m-%d")
        
        try:
            horoscopo = client.horoscopo_diario(
                carta_natal,
                fecha=fecha_str,
                timezone="America/Tegucigalpa"
            )
            
            # Análisis del día
            aspectos_positivos = sum(
                1 for a in horoscopo['top_aspects'] 
                if a['aspect'] in ['Trígono', 'Sextil']
            )
            aspectos_desafiantes = sum(
                1 for a in horoscopo['top_aspects'] 
                if a['aspect'] in ['Cuadratura', 'Oposición']
            )
            
            tono = "🟢 Favorable" if aspectos_positivos > aspectos_desafiantes else \
                   "🟡 Mixto" if aspectos_positivos == aspectos_desafiantes else \
                   "🟠 Desafiante"
            
            dia_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"][fecha.weekday()]
            
            print(f"{dia_semana} {fecha_str}: {tono} | "
                  f"{len(horoscopo['top_aspects'])} aspectos | "
                  f"{len(horoscopo['houses_activated'])} casas activadas")
            
            semana.append({
                "fecha": fecha_str,
                "tono": tono,
                "aspectos": horoscopo['top_aspects'][:3],
                "consejo": horoscopo['interpretation']['advice']
            })
            
        except Exception as e:
            print(f"❌ Error en {fecha_str}: {e}")
    
    # Guardar semana
    with open("horoscopo_semanal.json", "w", encoding="utf-8") as f:
        json.dump(semana, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Horóscopo semanal guardado en: horoscopo_semanal.json")


# =============================================================================
# EJEMPLO 5: Solo obtener tránsitos (sin carta natal)
# =============================================================================

def ejemplo_solo_transitos():
    """Obtener solo posiciones planetarias sin horóscopo personalizado"""
    print("\n" + "="*80)
    print("EJEMPLO 5: Solo Tránsitos Planetarios")
    print("="*80)
    
    client = AstroAPIClient()
    
    print("\n⏳ Obteniendo posiciones planetarias actuales...")
    transitos = client.obtener_transitos(timezone="America/Tegucigalpa")
    
    print(f"\n🌍 Tránsitos para {transitos['date']}")
    print("-" * 80)
    
    for planeta, data in transitos['transits'].items():
        retrograde = " ℞" if data['speed'] < 0 else ""
        print(f"{planeta.capitalize():12} | {data['sign']:12} | "
              f"{data['degree_in_sign']:6.2f}°{retrograde}")


# =============================================================================
# EJEMPLO 6: Integración con base de datos
# =============================================================================

def ejemplo_integracion_database():
    """Ejemplo de cómo integrar con una base de datos"""
    print("\n" + "="*80)
    print("EJEMPLO 6: Integración con Base de Datos (SQLite)")
    print("="*80)
    
    import sqlite3
    
    # Crear base de datos de ejemplo
    conn = sqlite3.connect("astro_users.db")
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            email TEXT,
            natal_chart_json TEXT,
            timezone TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_horoscopes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            fecha DATE,
            horoscope_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    
    client = AstroAPIClient()
    
    # Simular nuevo usuario
    print("\n1. Registrando nuevo usuario...")
    datos = {
        "datetime": "1992-12-07T23:58:00",
        "timezone": "America/Tegucigalpa",
        "latitude": 14.0723,
        "longitude": -87.1921,
        "house_system": "P",
        "topocentric_moon_only": False
    }
    
    carta_natal = client.calcular_carta_natal(datos)
    
    cursor.execute("""
        INSERT INTO users (nombre, email, natal_chart_json, timezone)
        VALUES (?, ?, ?, ?)
    """, ("Usuario Demo", "demo@example.com", json.dumps(carta_natal), "America/Tegucigalpa"))
    
    user_id = cursor.lastrowid
    conn.commit()
    print(f"   ✅ Usuario creado con ID: {user_id}")
    
    # Generar horóscopo diario
    print("\n2. Generando horóscopo diario...")
    horoscopo = client.horoscopo_diario(carta_natal, timezone="America/Tegucigalpa")
    
    cursor.execute("""
        INSERT INTO daily_horoscopes (user_id, fecha, horoscope_json)
        VALUES (?, ?, ?)
    """, (user_id, horoscopo['date'], json.dumps(horoscopo)))
    
    conn.commit()
    print(f"   ✅ Horóscopo guardado para {horoscopo['date']}")
    
    # Consultar histórico
    print("\n3. Consultando histórico...")
    cursor.execute("""
        SELECT fecha, horoscope_json FROM daily_horoscopes
        WHERE user_id = ?
        ORDER BY fecha DESC
    """, (user_id,))
    
    for fecha, horoscope_json in cursor.fetchall():
        h = json.loads(horoscope_json)
        print(f"   📅 {fecha}: {len(h['top_aspects'])} aspectos")
    
    conn.close()
    print("\n✅ Base de datos: astro_users.db")


# =============================================================================
# EJECUTAR EJEMPLOS
# =============================================================================

if __name__ == "__main__":
    import sys
    
    ejemplos = {
        "1": ("Uso básico - Horóscopo del día", ejemplo_basico),
        "2": ("Sistema con caché", ejemplo_con_cache),
        "3": ("Múltiples usuarios (batch)", ejemplo_multiple_usuarios),
        "4": ("Horóscopo semanal", ejemplo_horoscopo_semanal),
        "5": ("Solo tránsitos", ejemplo_solo_transitos),
        "6": ("Integración con BD", ejemplo_integracion_database),
    }
    
    if len(sys.argv) > 1:
        opcion = sys.argv[1]
        if opcion in ejemplos:
            titulo, func = ejemplos[opcion]
            print(f"\n🚀 Ejecutando: {titulo}")
            func()
        else:
            print(f"❌ Ejemplo '{opcion}' no encontrado")
    else:
        print("\n" + "="*80)
        print("🌟 EJEMPLOS DE USO - API DE HORÓSCOPO DIARIO")
        print("="*80)
        print("\nEjecutar con: python ejemplos_uso_api.py [número]\n")
        
        for num, (titulo, _) in ejemplos.items():
            print(f"  {num}. {titulo}")
        
        print("\nEjemplo: python ejemplos_uso_api.py 1")
        print("\nO ejecutar todos:\n")
        
        for _, func in ejemplos.values():
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error: {e}")
