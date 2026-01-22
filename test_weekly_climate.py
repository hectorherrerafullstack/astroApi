
import sys
import os
import django
import json
from datetime import date

# Add the 'backend' directory to sys.path so we can import 'api'
# Assuming the script is in 'astroapi/' and 'backend/' is a subdirectory.
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_path)

# Set the settings module. 
# Usually if manage.py is in backend/, and project name is 'backend', it's 'backend.settings' 
# BUT we need to be careful if 'backend' is also the package name.
# Let's try 'backend.settings' assuming 'backend' package exists inside 'backend' folder
# OR just 'settings' if it's flat.
# Based on previous output `Django version 4.2.18, using settings 'backend.settings'`, it IS 'backend.settings'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

from api.weekly_climate_service import calculate_weekly_climate

def test_weekly_climate():
    # Test with current week
    print("Calculando clima semanal...")
    result = calculate_weekly_climate()
    
    print("\n--- Cambios de Signo ---")
    changes = result.get('sign_changes', [])
    if not changes:
        print("No se detectaron cambios de signo esta semana.")
    else:
        for change in changes:
            print(f"{change['planet_es']} -> {change['to_sign']} el {change['date']} a las {change.get('time_utc', 'N/A')} UTC")
            
    print("\nJSON Completo (Preview):")
    print(json.dumps(changes, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_weekly_climate()
