from api.weekly_climate_service import calculate_weekly_climate
import json

print("\n--- INICIO TEST ---")
result = calculate_weekly_climate()

print("\n--- Cambios de Signo ---")
changes = result.get('sign_changes', [])
if not changes:
    print("No detects detected.")
else:
    for change in changes:
        print(f"{change['planet_es']} -> {change['to_sign']} el {change['date']} a las {change.get('time_utc', 'N/A')} UTC")

print("\n--- FIN TEST ---")
