#!/bin/bash
# Script para ejecutar tests de la nueva ruta /api/sun-transit/

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Tests para GET /api/sun-transit/                             ║"
echo "║  Ruta de Tránsito Diario del Sol                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navegar al directorio de Django
cd "$(dirname "$0")/.."

echo "Ejecutando tests de la API del tránsito solar..."
echo ""

# Ejecutar tests específicos
python manage.py test api.test_sun_transit.SunTransitDailyTestCase -v 2
python manage.py test api.test_sun_transit.SunTransitDataValidationTestCase -v 2
python manage.py test api.test_sun_transit.SunTransitPerformanceTestCase -v 2

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Tests completados                                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
