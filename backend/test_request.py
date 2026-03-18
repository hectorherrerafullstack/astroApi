
import requests
import json
import sys

try:
    url = 'http://127.0.0.1:8080/api/planet-transits/'
    payload = {
        'datetime': '2026-01-28T13:45:00',
        'timezone': 'Europe/Madrid',
        'latitude': 40.4168,
        'longitude': -3.7038,
        'house_system': 'P',
        'topocentric_moon_only': False
    }
    response = requests.post(url, json=payload)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
