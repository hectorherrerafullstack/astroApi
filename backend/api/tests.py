from django.test import TestCase
from django.conf import settings
from .services import compute_chart

class ChartTest(TestCase):
    def test_persona_1(self):
        payload = {
            "datetime": "1997-11-06T14:05:00",
            "timezone": "Europe/Madrid",
            "latitude": 41.5629623,
            "longitude": 2.0100492,
            "house_system": "placidus",
            "topocentric_moon_only": True
        }
        result = compute_chart(payload, settings.SE_EPHE_PATH)
        self.assertIn("planets", result)
        self.assertIn("houses", result)
        # Podrías comprobar tolerancias (±0.1°) comparando con valores conocidos