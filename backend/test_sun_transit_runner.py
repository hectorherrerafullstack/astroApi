#!/usr/bin/env python
"""
Script para ejecutar tests de la ruta /api/sun-transit/
Uso: python test_sun_transit_runner.py
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

if __name__ == "__main__":
    from django.core.management import call_command
    
    print("\n" + "="*70)
    print("TESTS PARA LA RUTA /api/sun-transit/")
    print("="*70 + "\n")
    
    # Ejecutar todos los tests de sun_transit
    print("Ejecutando tests de funcionalidad...")
    print("-" * 70)
    call_command('test', 'api.test_sun_transit', '-v', '2')
    
    print("\n" + "="*70)
    print("✅ TESTS COMPLETADOS")
    print("="*70 + "\n")
