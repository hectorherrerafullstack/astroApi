
import os
import sys
import json
from pathlib import Path

# Add backend to path so we can import api modules
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

# Setup Django minimal (needed if service imports django stuff? Service imports .services which is pure python + swe)
# But it imports from .services, so relative import might fail if run as script.
# Better to run as module: python -m backend.api.test_acg_service
# or adjust sys.path and remove relative imports in favor of absolute if needed, or keep relative and run from root.

# Let's try to simulate the direct import of the function
# We need to hack the path to make 'api' importable or 'backend.api'
# If run from 'c:\Users\hecto\Desktop\escritorio\astroapi', 'backend' is a package.

try:
    from backend.api.astrocartography_service import process_astrocartography_mundane
except ImportError:
    # Fallback if run from inside api folder
    sys.path.append(str(BASE_DIR / "backend"))
    from api.astrocartography_service import process_astrocartography_mundane

payload = {
    "datetime": "2024-01-01T12:00:00",
    "lat": 40.4168, 
    "lng": -3.7038,
    "targets": [
        {
            "name": "Madrid",
            "lat": 40.4168,
            "lng": -3.7038
        },
        {
            "name": "New York",
            "lat": 40.7128,
            "lng": -74.0060
        },
        {
            "name": "Tokyo",
            "lat": 35.6762,
            "lng": 139.6503
        }
    ]
}

print("--- TESTING ACG SERVICE ---")
try:
    result = process_astrocartography_mundane(payload)
    print(json.dumps(result, indent=2, default=str))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
