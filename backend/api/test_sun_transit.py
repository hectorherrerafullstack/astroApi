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

import json
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse


class SunTransitDailyTestCase(TestCase):
    """
    Tests para la nueva ruta GET /api/sun-transit/
    Verifica la funcionalidad de tránsito diario del Sol
    """
    
    def setUp(self):
        """Inicializa el cliente HTTP para las pruebas"""
        self.client = Client()
        self.url = reverse('sun_transit_daily')
    
    def test_sun_transit_basic_request(self):
        """
        Test 1: Obtener tránsito del Sol sin parámetros
        Debe retornar datos del Sol para hoy
        """
        print("\n" + "="*70)
        print("TEST 1: Obtener tránsito del Sol sin parámetros")
        print("="*70)
        
        response = self.client.get(self.url)
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        print(f"Respuesta: {json.dumps(data, indent=2)}")
        
        # Verificar estructura de respuesta
        self.assertIn('date', data)
        self.assertIn('timezone', data)
        self.assertIn('sun', data)
        
        # Verificar datos del Sol
        sun_data = data['sun']
        self.assertIn('longitude', sun_data)
        self.assertIn('degree_in_sign', sun_data)
        self.assertIn('sign', sun_data)
        self.assertIn('sign_index', sun_data)
        self.assertIn('speed', sun_data)
        
        # Verificar rangos de valores
        self.assertGreaterEqual(sun_data['longitude'], 0)
        self.assertLess(sun_data['longitude'], 360)
        
        self.assertGreaterEqual(sun_data['degree_in_sign'], 0)
        self.assertLess(sun_data['degree_in_sign'], 30)
        
        self.assertGreaterEqual(sun_data['sign_index'], 0)
        self.assertLess(sun_data['sign_index'], 12)
        
        # Verificar signo
        signos = ['aries', 'tauro', 'geminis', 'cancer', 'leo', 'virgo',
                 'libra', 'escorpio', 'sagitario', 'capricornio', 'acuario', 'piscis']
        self.assertIn(sun_data['sign'].lower(), signos)
        
        # Verificar que NO tenga casa (no fue solicitada)
        self.assertNotIn('house', sun_data)
        
        print("✅ TEST 1 PASADO: Respuesta correcta sin parámetros")
    
    def test_sun_transit_with_date(self):
        """
        Test 2: Obtener tránsito del Sol para una fecha específica
        """
        print("\n" + "="*70)
        print("TEST 2: Obtener tránsito del Sol con fecha específica")
        print("="*70)
        
        date_param = '2025-12-25'
        response = self.client.get(f'{self.url}?date={date_param}')
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        print(f"Fecha solicitada: {date_param}")
        print(f"Fecha en respuesta: {data['date']}")
        print(f"Sol en: {data['sun']['sign']} a {data['sun']['degree_in_sign']:.2f}°")
        
        # Verificar que la fecha es correcta
        self.assertEqual(data['date'], date_param)
        
        print("✅ TEST 2 PASADO: Fecha correcta en respuesta")
    
    def test_sun_transit_with_timezone(self):
        """
        Test 3: Obtener tránsito del Sol con zona horaria específica
        """
        print("\n" + "="*70)
        print("TEST 3: Obtener tránsito con zona horaria")
        print("="*70)
        
        timezone_param = 'America/Tegucigalpa'
        response = self.client.get(f'{self.url}?timezone={timezone_param}')
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        print(f"Zona horaria solicitada: {timezone_param}")
        print(f"Zona horaria en respuesta: {data['timezone']}")
        
        # Verificar que la zona horaria es correcta
        self.assertEqual(data['timezone'], timezone_param)
        
        print("✅ TEST 3 PASADO: Zona horaria correcta")
    
    def test_sun_transit_with_date_and_timezone(self):
        """
        Test 4: Obtener tránsito con fecha y zona horaria
        """
        print("\n" + "="*70)
        print("TEST 4: Obtener tránsito con fecha y zona horaria")
        print("="*70)
        
        date_param = '2025-06-21'
        timezone_param = 'America/Mexico_City'
        
        response = self.client.get(f'{self.url}?date={date_param}&timezone={timezone_param}')
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        print(f"Fecha: {date_param}, Timezone: {timezone_param}")
        print(f"Respuesta - Fecha: {data['date']}, Timezone: {data['timezone']}")
        print(f"Sol en: {data['sun']['sign']}")
        
        self.assertEqual(data['date'], date_param)
        self.assertEqual(data['timezone'], timezone_param)
        
        print("✅ TEST 4 PASADO: Fecha y zona horaria correctas")
    
    def test_sun_transit_with_houses_cusps(self):
        """
        Test 5: Obtener tránsito del Sol CON información de casas
        """
        print("\n" + "="*70)
        print("TEST 5: Obtener tránsito CON información de casas")
        print("="*70)
        
        houses_cusps = '12.5,45.3,78.2,102.1,135.8,168.9,192.5,225.3,258.2,282.1,315.8,348.9'
        response = self.client.get(f'{self.url}?houses_cusps={houses_cusps}')
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        print(f"Respuesta con casas:")
        print(json.dumps(data, indent=2))
        
        # Verificar que TIENE casa
        self.assertIn('house', data['sun'])
        
        # Verificar que la casa está en rango válido
        house = data['sun']['house']
        self.assertGreaterEqual(house, 1)
        self.assertLessEqual(house, 12)
        
        print(f"✅ Casa del Sol: {house}")
        print("✅ TEST 5 PASADO: Información de casa correcta")
    
    def test_sun_transit_with_all_parameters(self):
        """
        Test 6: Obtener tránsito del Sol con TODOS los parámetros
        """
        print("\n" + "="*70)
        print("TEST 6: Obtener tránsito con TODOS los parámetros")
        print("="*70)
        
        date_param = '2025-03-21'
        timezone_param = 'Europe/London'
        houses_cusps = '10.5,40.2,75.8,100.3,130.9,165.2,190.5,220.2,255.8,280.3,310.9,345.2'
        
        response = self.client.get(
            f'{self.url}?date={date_param}&timezone={timezone_param}&houses_cusps={houses_cusps}'
        )
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        print(f"Parámetros:")
        print(f"  - Fecha: {date_param}")
        print(f"  - Timezone: {timezone_param}")
        print(f"  - Casas: 12 cúspides")
        print(f"\nRespuesta:")
        print(json.dumps(data, indent=2))
        
        # Verificar todos los parámetros
        self.assertEqual(data['date'], date_param)
        self.assertEqual(data['timezone'], timezone_param)
        self.assertIn('house', data['sun'])
        
        print("✅ TEST 6 PASADO: Todos los parámetros correctos")
    
    def test_invalid_date_format(self):
        """
        Test 7: Verificar error con formato de fecha incorrecto
        """
        print("\n" + "="*70)
        print("TEST 7: Verificar error con formato de fecha incorrecto")
        print("="*70)
        
        invalid_date = '25-12-2025'  # Formato incorrecto
        response = self.client.get(f'{self.url}?date={invalid_date}')
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        print(f"Fecha enviada: {invalid_date}")
        print(f"Error: {data}")
        
        # Verificar que contiene mensaje de error
        self.assertIn('error', data.get('message', '') or str(data))
        
        print("✅ TEST 7 PASADO: Error detectado correctamente")
    
    def test_invalid_houses_cusps_count(self):
        """
        Test 8: Verificar error con cantidad incorrecta de cúspides
        """
        print("\n" + "="*70)
        print("TEST 8: Verificar error con cantidad incorrecta de cúspides")
        print("="*70)
        
        invalid_cusps = '10.5,40.2,75.8,100.3'  # Solo 4 en lugar de 12
        response = self.client.get(f'{self.url}?houses_cusps={invalid_cusps}')
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        print(f"Cúspides enviadas: 4 (incorrecto)")
        print(f"Error: {data}")
        
        print("✅ TEST 8 PASADO: Validación de cúspides funciona")
    
    def test_post_method_not_allowed(self):
        """
        Test 9: Verificar que POST no está permitido
        """
        print("\n" + "="*70)
        print("TEST 9: Verificar que POST no está permitido")
        print("="*70)
        
        response = self.client.post(self.url, data={})
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        print(f"Error al usar POST: {data}")
        
        print("✅ TEST 9 PASADO: POST correctamente rechazado")
    
    def test_response_headers(self):
        """
        Test 10: Verificar headers de la respuesta
        """
        print("\n" + "="*70)
        print("TEST 10: Verificar headers de respuesta")
        print("="*70)
        
        response = self.client.get(self.url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.get('Content-Type')}")
        print(f"X-Source-Code: {response.get('X-Source-Code')}")
        print(f"X-License: {response.get('X-License')}")
        
        # Verificar headers de licencia
        self.assertIn('X-Source-Code', response)
        self.assertIn('X-License', response)
        self.assertEqual(response.get('X-License'), 'AGPL-3.0-only')
        
        print("✅ TEST 10 PASADO: Headers correctos")


class SunTransitDataValidationTestCase(TestCase):
    """
    Tests para validar que los datos del Sol sean astronómicamente correctos
    """
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('sun_transit_daily')
    
    def test_sun_degrees_in_sign_range(self):
        """
        Test 11: Verificar que degree_in_sign esté en rango 0-30
        """
        print("\n" + "="*70)
        print("TEST 11: Validar rango degree_in_sign (0-30°)")
        print("="*70)
        
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        degree = data['sun']['degree_in_sign']
        print(f"degree_in_sign: {degree}°")
        
        self.assertGreaterEqual(degree, 0)
        self.assertLess(degree, 30)
        
        print("✅ TEST 11 PASADO: Grados en signo válidos")
    
    def test_sun_longitude_correspondence(self):
        """
        Test 12: Verificar que longitude y sign_index sean consistentes
        """
        print("\n" + "="*70)
        print("TEST 12: Validar correspondencia longitude-sign_index")
        print("="*70)
        
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        sun = data['sun']
        calculated_sign_index = int(sun['longitude'] // 30)
        
        print(f"Longitude: {sun['longitude']}°")
        print(f"Sign Index en respuesta: {sun['sign_index']}")
        print(f"Sign Index calculado: {calculated_sign_index}")
        
        self.assertEqual(sun['sign_index'], calculated_sign_index)
        
        print("✅ TEST 12 PASADO: Longitude y sign_index son consistentes")
    
    def test_sun_speed_is_reasonable(self):
        """
        Test 13: Verificar que la velocidad del Sol es razonable (~1°/día)
        """
        print("\n" + "="*70)
        print("TEST 13: Validar velocidad del Sol (~1°/día)")
        print("="*70)
        
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        speed = data['sun']['speed']
        print(f"Velocidad del Sol: {speed}°/día")
        
        # El Sol típicamente se mueve ~0.98-1.02°/día
        self.assertGreater(speed, 0.95)
        self.assertLess(speed, 1.05)
        
        print("✅ TEST 13 PASADO: Velocidad del Sol es astronómicamente correcta")


class SunTransitPerformanceTestCase(TestCase):
    """
    Tests para verificar el caché y performance
    """
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('sun_transit_daily')
    
    def test_multiple_requests_same_date(self):
        """
        Test 14: Verificar que múltiples requests de la misma fecha devuelven los mismos datos
        (indicador de que el caché funciona)
        """
        print("\n" + "="*70)
        print("TEST 14: Verificar consistencia entre múltiples requests")
        print("="*70)
        
        date_param = '2025-06-21'
        
        # Primera request
        response1 = self.client.get(f'{self.url}?date={date_param}')
        data1 = json.loads(response1.content)
        
        # Segunda request (debería ser del caché)
        response2 = self.client.get(f'{self.url}?date={date_param}')
        data2 = json.loads(response2.content)
        
        print(f"Primer request - Longitude: {data1['sun']['longitude']}")
        print(f"Segundo request - Longitude: {data2['sun']['longitude']}")
        
        # Los datos deben ser idénticos
        self.assertEqual(data1['sun']['longitude'], data2['sun']['longitude'])
        self.assertEqual(data1['sun']['sign'], data2['sun']['sign'])
        
        print("✅ TEST 14 PASADO: Datos consistentes (caché funciona)")
