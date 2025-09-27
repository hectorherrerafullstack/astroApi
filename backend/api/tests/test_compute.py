# backend/api/tests/test_compute.py
from django.test import TestCase
from django.urls import reverse
import json

class ComputeAPITest(TestCase):
    def test_persona_ejemplo(self):
        url = reverse("compute_chart")
        payload = {
            "datetime": "1992-02-14T20:30:00",
            "timezone": "Europe/Madrid",
            "latitude": 41.5421,
            "longitude": 2.1094,
            "house_system": "placidus",
            "topocentric_moon_only": False
        }
        r = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("planets", data)
        self.assertIn("houses", data)
        self.assertIn("aspects", data)
        # Ejemplo: verificar que el Sol esté en Acuario (~325°)
        self.assertAlmostEqual(data["planets"]["sun"]["value"], 325.0, delta=1.0)