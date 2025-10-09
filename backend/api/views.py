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
from .services import compute_chart
from .horoscope_service import generate_daily_horoscope_personal, calculate_transits

REPO_URL = os.environ.get("SOURCE_REPO_URL", "https://github.com/tuusuario/astro-backend")

def health(request):
    resp = JsonResponse({"status": "ok"})
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
    
    Retorna posiciones planetarias (tránsitos) para una fecha/hora.
    Si no se especifica fecha, usa el momento actual.
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
        transits = calculate_transits(target_date, timezone)
        result = {
            "date": target_date.strftime("%Y-%m-%d"),
            "timezone": timezone,
            "transits": transits
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