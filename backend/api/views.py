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

import os
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .services import compute_chart, get_important_transits, calculate_eclipses, fmt_zodiac
from .weekly_climate_service import calculate_weekly_climate
from .horoscope_service import generate_daily_horoscope_personal, calculate_transits, find_house_for_planet, get_daily_planetary_data, get_next_moon_ingress, get_moon_realtime
from .weekly_climate_service import calculate_weekly_climate

REPO_URL = os.environ.get("SOURCE_REPO_URL", "https://github.com/tuusuario/astro-backend")

def health(request):
    resp = JsonResponse({
        "status": "ok",
        "version": "2026-01-21-v6",  # Para verificar deploy
        "fix": "weekly_climate_phase_precision"
    })
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp

def compute_chart_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST with JSON payload.")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON.")

    # Validate required fields
    required_fields = ["datetime", "timezone", "latitude", "longitude", "house_system", "topocentric_moon_only"]
    for field in required_fields:
        if field not in payload:
            return HttpResponseBadRequest(f"Missing required field: {field}")

    try:
        result = compute_chart(payload, settings.SE_EPHE_PATH)
    except Exception as e:
        return HttpResponseBadRequest(f"Calculation error: {str(e)}")

    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


def planet_transits_view(request):
    """
    POST /api/planet-transits/
    
    Acts exactly like /api/compute/, but includes request context in response.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST with JSON payload.")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON.")

    # Validate required fields
    required_fields = ["datetime", "timezone", "latitude", "longitude", "house_system", "topocentric_moon_only"]
    for field in required_fields:
        if field not in payload:
            return HttpResponseBadRequest(f"Missing required field: {field}")

    try:
        # Calculate chart
        result = compute_chart(payload, settings.SE_EPHE_PATH)
        
        # Inject context directly into the response root
        result["request_datetime"] = payload["datetime"]
        result["request_timezone"] = payload["timezone"]
        result["request_location"] = {
            "latitude": payload["latitude"],
            "longitude": payload["longitude"]
        }
        
        # Customization per user request:
        # 1. Remove houses, Ascendant, MC
        if "houses" in result:
            del result["houses"]
            
        if "aspects" in result:
            del result["aspects"]
            
        # 2. Add South Node (Calculated from True Node)
        if "true_node" in result["planets"]:
            tn_val = result["planets"]["true_node"]["value"]
            tn_speed = result["planets"]["true_node"]["speed"]
            sn_val = (tn_val + 180.0) % 360.0
            
            result["planets"]["south_node"] = {
                "value": sn_val,
                "speed": tn_speed, # Same speed as North Node
                "retrograde": result["planets"]["true_node"]["retrograde"],
                "formatted": fmt_zodiac(sn_val) + (" ℞" if tn_speed < 0 else "")
            }

    except Exception as e:
        return HttpResponseBadRequest(f"Calculation error: {str(e)}")


    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


def daily_horoscope_view(request):
    """
    POST /api/horoscope/daily/
    
    Payload:
    {
        "birth_data": {
            // Carta natal completa (output de /api/compute/)
            "planets": {...},
            "houses": {...}
        },
        "target_date": "2025-10-09",  // opcional, default: hoy
        "timezone": "America/Tegucigalpa"  // opcional, default: UTC
    }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST with JSON payload.")
    
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON.")
    
    # Validar carta natal
    if "birth_data" not in payload:
        return HttpResponseBadRequest("Missing 'birth_data' field.")
    
    birth_data = payload["birth_data"]
    if "planets" not in birth_data or "houses" not in birth_data:
        return HttpResponseBadRequest("birth_data must contain 'planets' and 'houses'.")
    
    # Fecha objetivo (default: hoy)
    target_date_str = payload.get("target_date")
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        except ValueError:
            return HttpResponseBadRequest("Invalid target_date format. Use YYYY-MM-DD.")
    else:
        target_date = datetime.now()
    
    timezone = payload.get("timezone", "UTC")
    
    try:
        result = generate_daily_horoscope_personal(birth_data, target_date, timezone)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


def transits_view(request):
    """
    GET /api/transits/?date=YYYY-MM-DD&timezone=America/Tegucigalpa
    
    Retorna la posición de la Luna (tránsito lunar) para una fecha/hora.
    Si no se especifica fecha, usa el momento actual.
    """
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET request.")
    
    date_str = request.GET.get("date")
    # Admitimos 'time' (genérico) o 'birth_time' (si viene del frontend de carta natal)
    time_str = request.GET.get("time") or request.GET.get("birth_time")
    timezone = request.GET.get("timezone", "UTC")
    
    force_utc = False
    
    if date_str:
        try:
            # Parse date
            dt_part = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Parse time if provided, else default to 00:00:00
            if time_str:
                try:
                    # Intenta formatos completos y cortos
                    if len(time_str.split(":")) == 2:
                        t_part = datetime.strptime(time_str, "%H:%M").time()
                    else:
                        t_part = datetime.strptime(time_str, "%H:%M:%S").time()
                except ValueError:
                    return HttpResponseBadRequest("Invalid time/birth_time format. Use HH:MM or HH:MM:SS.")
            else:
                t_part = datetime.min.time() # 00:00:00
            
            target_date = datetime.combine(dt_part.date(), t_part)
            
            # NOTA: Ya no forzamos UTC si es hoy, respetamos la fecha/hora pedida.
            
        except ValueError:
            return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD.")
    else:
        target_date = datetime.utcnow()
        force_utc = True
    
    try:
        # Si usamos la hora actual UTC, forzamos la zona horaria a UTC para el cálculo
        calc_timezone = "UTC" if force_utc else timezone
        
        # Usar cálculo en tiempo real para la Luna (sin caché)
        moon_data = get_moon_realtime(target_date, calc_timezone)
        next_ingress = get_next_moon_ingress(target_date, calc_timezone)
        
        result = {
            "date": target_date.strftime("%Y-%m-%d"),
            "timezone": timezone,
            "server_time_utc": target_date.strftime("%H:%M:%S"),
            "calculation_timezone": calc_timezone,
            **moon_data,
            "next_ingress": next_ingress
        }
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


def monthly_transits_view(request, month, year):
    """
    GET /api/monthly-transits/<int:month>/<int:year>/
    
    Retorna la posición de la Luna para cada día del mes.
    """
    try:
        month = int(month)
        year = int(year)
        if not (1 <= month <= 12) or not (1900 <= year <= 2100):
            return HttpResponseBadRequest("Invalid month or year.")
        
        from calendar import monthrange
        days_in_month = monthrange(year, month)[1]
        daily_moon = []
        for day in range(1, days_in_month + 1):
            sample_date = datetime(year=year, month=month, day=day)
            try:
                moon_transits = calculate_transits(sample_date, "UTC")
                moon_data = moon_transits.get("moon", {})
                daily_moon.append({
                    "date": sample_date.strftime("%Y-%m-%d"),
                    **moon_data
                })
            except Exception:
                pass
        
        result = {
            "month": month,
            "year": year,
            "daily_moon": daily_moon
        }
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


def cache_stats_view(request):
    """
    GET /api/cache/stats/
    
    Retorna estadísticas de caché y performance.
    """
    from .cache_manager import performance_monitor, SmartCache
    
    stats = {
        "performance": performance_monitor.get_report(),
        "cache": SmartCache.get_cache_stats(),
        "info": {
            "cache_backend": "LocMemCache",
            "compression": "gzip enabled",
            "ttl_transits": "1 hour",
            "ttl_horoscope": "6 hours",
            "ttl_natal": "30 days"
        }
    }
    
    resp = JsonResponse(stats, json_dumps_params={"ensure_ascii": False, "indent": 2})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


@api_view(["GET"])
@permission_classes([AllowAny])
def sun_transit_daily_view(request):
    """
    GET /api/sun-transit/?birth_datetime=YYYY-MM-DDTHH:MM&latitude=XX.XX&longitude=XX.XX
    
    Retorna el signo y la casa del Sol HOY en tu carta natal.
    
    Parámetros REQUERIDOS:
        - birth_datetime: Fecha y hora de nacimiento (YYYY-MM-DDTHH:MM)
        - latitude: Latitud de nacimiento
        - longitude: Longitud de nacimiento
    
    Retorna:
        {
            "sign": "Escorpio",
            "degree": 15.45,
            "house": 7
        }
    """
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET request.")
    
    # Obtener parámetros de nacimiento (REQUERIDOS)
    birth_datetime_str = request.GET.get("birth_datetime")
    latitude_str = request.GET.get("latitude")
    longitude_str = request.GET.get("longitude")
    
    if not all([birth_datetime_str, latitude_str, longitude_str]):
        return HttpResponseBadRequest(
            "Missing required parameters. Need: birth_datetime, latitude, longitude"
        )
    
    # Validar y parsear datos de nacimiento
    try:
        birth_datetime = datetime.strptime(birth_datetime_str, "%Y-%m-%dT%H:%M")
        latitude = float(latitude_str)
        longitude = float(longitude_str)
    except ValueError as e:
        return HttpResponseBadRequest(f"Invalid parameter format: {str(e)}")
    
    # Usar valores fijos para el tránsito
    target_date = datetime.now()
    timezone = "UTC"
    house_system = "P"
    
    try:
        # 1. Calcular la carta natal para obtener las cúspides de las casas
        natal_data = {
            "datetime": birth_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
            "house_system": house_system,
            "topocentric_moon_only": False
        }
        natal_chart = compute_chart(natal_data, settings.SE_EPHE_PATH)
        cusps_data = natal_chart.get("houses", {}).get("cusps", [])
        # Extraer solo los valores numéricos de las cúspides
        houses_cusps = [c.get("value") for c in cusps_data]
        
        # 2. Calcular el tránsito del Sol HOY
        transits = calculate_transits(target_date, timezone)
        sun_data = transits.get("sun", {})
        
        # 3. Encontrar en qué casa está el Sol
        house_num = find_house_for_planet(sun_data.get("longitude", 0), houses_cusps)
        
        # Respuesta simplificada
        result = {
            "sign": sun_data.get("sign"),
            "degree": sun_data.get("degree_in_sign"),
            "house": house_num
        }
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


@api_view(["GET"])
@permission_classes([AllowAny])
def weekly_climate_view(request):
    """
    GET /api/weekly-climate/
    GET /api/weekly-climate/?start_date=2026-01-05&timezone=Europe/Madrid
    
    Retorna los datos del clima astral semanal:
    - request_time: Hora de la petición en la zona horaria del usuario
    - Fase lunar principal
    - Cambios de signo (TODOS los cuerpos celestes con hora exacta)
    - Cambios retro/directo
    - Aspectos fuertes priorizados (máx. 4)
    - Posiciones planetarias, asteroides y Lilith
    """
    from datetime import date
    from dateutil import tz as dateutil_tz
    
    # Parámetro opcional: start_date
    start_date_str = request.GET.get("start_date")
    # Parámetro opcional: timezone (default UTC)
    timezone_str = request.GET.get("timezone", "UTC")
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponseBadRequest(
                "Invalid start_date format. Use YYYY-MM-DD."
            )
    else:
        start_date = None  # Usará la semana actual
    
    # Validar timezone
    user_tz = dateutil_tz.gettz(timezone_str)
    if user_tz is None:
        return HttpResponseBadRequest(
            f"Invalid timezone: {timezone_str}. Use IANA format like 'Europe/Madrid'."
        )
    
    try:
        result = calculate_weekly_climate(start_date)
        
        # Añadir hora de la petición en la zona horaria del usuario
        now_utc = datetime.now(dateutil_tz.UTC)
        now_local = now_utc.astimezone(user_tz)
        
        result["request_info"] = {
            "request_time_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%S"),
            "request_time_local": now_local.strftime("%Y-%m-%dT%H:%M:%S"),
            "timezone": timezone_str
        }
        
        # Convertir las horas de cambios de signo a la zona horaria del usuario
        if "sign_changes" in result:
            for change in result["sign_changes"]:
                if "datetime_utc" in change:
                    # Parsear la fecha UTC y convertir a local
                    dt_utc = datetime.fromisoformat(change["datetime_utc"])
                    dt_utc = dt_utc.replace(tzinfo=dateutil_tz.UTC)
                    dt_local = dt_utc.astimezone(user_tz)
                    change["time_local"] = dt_local.strftime("%H:%M")
                    change["datetime_local"] = dt_local.strftime("%Y-%m-%dT%H:%M:%S")
        
    except Exception as e:
        print(f"ERROR in weekly_climate_view: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


@api_view(["GET"])
@permission_classes([AllowAny])
def daily_planetary_positions_view(request):
    """
    GET /api/daily-positions/?date=YYYY-MM-DD&timezone=UTC
    
    Retorna posiciones planetarias y aspectos mundanos para el día.
    No requiere carta natal.
    """
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET request.")
    
    date_str = request.GET.get("date")
    timezone = request.GET.get("timezone", "UTC")
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD.")
    else:
        target_date = datetime.now()
    
    try:
        result = get_daily_planetary_data(target_date, timezone)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp


@api_view(["GET"])
@permission_classes([AllowAny])
def eclipses_view(request):
    """
    GET /api/eclipses/?year=2026
    
    Retorna lista de eclipses (solares y lunares) para el año dado.
    """
    year_str = request.GET.get("year")
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            return HttpResponseBadRequest("Invalid year format.")
    else:
        year = datetime.now().year
    
    try:
        eclipses = calculate_eclipses(year)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    resp = JsonResponse({"year": year, "eclipses": eclipses}, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp

@api_view(["POST"])
@permission_classes([AllowAny])
def mundane_astrocartography_view(request):
    """
    POST /api/astrocartography/mundane/
    
    Payload:
    {
        "datetime": "YYYY-MM-DDTHH:MM:SS",
        "lat": 0.0,
        "lng": 0.0,
        "targets": [
            {"name": "Madrid", "lat": 40.41, "lng": -3.70},
            ...
        ]
    }
    
    Retorna lista de planetas angulares (Mundanos y Zodiacales) con Parans.
    """
    from .astrocartography_service import process_astrocartography_mundane
    
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON.")
        
    required = ["datetime", "lat", "lng", "targets"]
    if not all(k in payload for k in required):
        return HttpResponseBadRequest(f"Missing required fields. Need: {required}")
        
    try:
        result = process_astrocartography_mundane(payload)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
        
    resp = JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    resp["X-Source-Code"] = REPO_URL
    resp["X-License"] = "AGPL-3.0-only"
    return resp
