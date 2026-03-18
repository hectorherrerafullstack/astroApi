import requests, json, sys

try:
    # Force UTF-8 for stdout
    sys.stdout.reconfigure(encoding='utf-8')
    
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
    response.raise_for_status()
    
    # Save to file to avoid console encoding issues completely
    with open('final_response.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2, ensure_ascii=False)
        
    print("SUCCESS")
    
except Exception as e:
    print(f"ERROR: {e}")
