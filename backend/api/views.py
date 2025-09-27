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
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from .services import compute_chart

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