# This file is part of astroapi.
#
# astroapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Middleware personalizado para optimización de performance.
"""

from django.utils.cache import patch_cache_control
from django.utils.deprecation import MiddlewareMixin
import time


class PerformanceMiddleware(MiddlewareMixin):
    """
    Middleware que agrega headers de performance y caché.
    """
    
    def process_request(self, request):
        """Marca tiempo de inicio"""
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """Agrega headers de performance y caché"""
        
        # Calcular tiempo de respuesta
        if hasattr(request, '_start_time'):
            duration = (time.time() - request._start_time) * 1000  # ms
            response['X-Response-Time'] = f"{duration:.2f}ms"
        
        # Headers de caché según el endpoint
        path = request.path
        
        if '/api/transits/' in path:
            # Tránsitos: cacheable por 1 hora
            patch_cache_control(
                response,
                public=True,
                max_age=3600,
                s_maxage=3600
            )
        
        elif '/api/horoscope/daily/' in path:
            # Horóscopo diario: cacheable por 6 horas
            patch_cache_control(
                response,
                public=True,
                max_age=3600 * 6,
                s_maxage=3600 * 6
            )
        
        elif '/api/compute/' in path:
            # Carta natal: cacheable por 30 días
            patch_cache_control(
                response,
                public=True,
                max_age=86400 * 30,
                s_maxage=86400 * 30
            )
        
        # Header de indicador de caché
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if response.data.get('_from_cache'):
                response['X-Cache-Status'] = 'HIT'
            else:
                response['X-Cache-Status'] = 'MISS'
        
        return response


class CORSMiddleware(MiddlewareMixin):
    """
    Middleware CORS optimizado para APIs públicas.
    """
    
    def process_response(self, request, response):
        """Agrega headers CORS"""
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        response['Access-Control-Max-Age'] = '86400'  # 24 horas
        
        return response
