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
        
        # Verificar que los planetas incluyen info de retrógrado
        self.assertIn("retrograde", data["planets"]["sun"])
        self.assertIn("speed", data["planets"]["sun"])
        
        # Verificar ascendente y MC
        self.assertIn("ascendente", data["houses"])
        self.assertIn("mc", data["houses"])
        
        # Verificar Lilith
        self.assertIn("lilith", data["planets"])
        
        # Ejemplo: verificar que el Sol esté en Acuario (~325°)
        self.assertAlmostEqual(data["planets"]["sun"]["value"], 325.0, delta=1.0)
    
    def test_tegucigalpa_1992(self):
        """Persona nacida el 12 de julio de 1992 a las 23:58 en Tegucigalpa, Honduras"""
        url = reverse("compute_chart")
        payload = {
            "datetime": "1992-07-12T23:58:00",
            "timezone": "America/Tegucigalpa",
            "latitude": 14.0723,
            "longitude": -87.1921,
            "house_system": "placidus",
            "topocentric_moon_only": False
        }
        r = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        
        # Verificaciones básicas
        self.assertIn("planets", data)
        self.assertIn("houses", data)
        self.assertIn("aspects", data)
        
        # Verificar elementos clave
        self.assertIn("sun", data["planets"])
        self.assertIn("moon", data["planets"])
        self.assertIn("lilith", data["planets"])
        self.assertIn("ascendente", data["houses"])
        self.assertIn("mc", data["houses"])
        
        print("\n=== Tegucigalpa 12/07/1992 23:58 ===")
        print(f"Sol: {data['planets']['sun']['formatted']} (Retrógrado: {data['planets']['sun']['retrograde']})")
        print(f"Luna: {data['planets']['moon']['formatted']} (Retrógrado: {data['planets']['moon']['retrograde']})")
        print(f"Ascendente: {data['houses']['ascendente']['formatted']}")
        print(f"MC: {data['houses']['mc']['formatted']}")
        print(f"Lilith: {data['planets']['lilith']['formatted']} (Retrógrado: {data['planets']['lilith']['retrograde']})")
        print(f"Aspectos encontrados: {len(data['aspects'])}")