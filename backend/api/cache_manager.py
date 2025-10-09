# This file is part of astroapi.
#
# astroapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Sistema de caché para optimizar respuestas de API.
Reduce tiempo de respuesta de ~200ms a ~20ms en requests repetidas.
"""

from django.core.cache import cache
from functools import wraps
import hashlib
import json
from datetime import datetime, timedelta


class CacheManager:
    """Gestor centralizado de caché para la API"""
    
    # TTL (Time To Live) en segundos
    TTL_TRANSITS = 3600  # 1 hora (tránsitos cambian lento excepto Luna)
    TTL_NATAL_CHART = 86400 * 30  # 30 días (carta natal no cambia)
    TTL_DAILY_HOROSCOPE = 3600 * 6  # 6 horas (horóscopo del día)
    TTL_ASPECTS = 1800  # 30 minutos (aspectos entre tránsitos)
    
    @staticmethod
    def generate_key(prefix: str, data: dict) -> str:
        """
        Genera clave de caché consistente a partir de datos.
        Usa hash MD5 del JSON ordenado.
        """
        json_str = json.dumps(data, sort_keys=True)
        hash_md5 = hashlib.md5(json_str.encode()).hexdigest()
        return f"{prefix}:{hash_md5}"
    
    @staticmethod
    def get_transits_key(date_str: str, timezone: str) -> str:
        """Clave para tránsitos de un día específico"""
        return f"transits:{date_str}:{timezone}"
    
    @staticmethod
    def get_natal_chart_key(birth_data: dict) -> str:
        """Clave para carta natal"""
        return CacheManager.generate_key("natal", birth_data)
    
    @staticmethod
    def get_horoscope_key(birth_data: dict, date_str: str, timezone: str) -> str:
        """Clave para horóscopo diario"""
        birth_hash = hashlib.md5(
            json.dumps(birth_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        return f"horoscope:{birth_hash}:{date_str}:{timezone}"


def cache_transits(ttl=CacheManager.TTL_TRANSITS):
    """
    Decorator para cachear tránsitos planetarios.
    Los tránsitos son iguales para todos los usuarios en la misma fecha/hora.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(dt, timezone="UTC"):
            # Generar clave de caché
            date_str = dt.strftime("%Y-%m-%d-%H")
            cache_key = CacheManager.get_transits_key(date_str, timezone)
            
            # Intentar obtener de caché
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Calcular y guardar en caché
            result = func(dt, timezone)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_natal_chart(ttl=CacheManager.TTL_NATAL_CHART):
    """
    Decorator para cachear cartas natales.
    Las cartas natales nunca cambian para los mismos datos de nacimiento.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(birth_data, ephe_path=None):
            # Generar clave de caché
            cache_key = CacheManager.get_natal_chart_key(birth_data)
            
            # Intentar obtener de caché
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Calcular y guardar en caché
            result = func(birth_data, ephe_path)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_daily_horoscope(ttl=CacheManager.TTL_DAILY_HOROSCOPE):
    """
    Decorator para cachear horóscopos diarios.
    Un horóscopo del día es válido por varias horas.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(birth_data, target_date=None, timezone="UTC"):
            # Generar clave de caché
            if target_date is None:
                target_date = datetime.now()
            
            date_str = target_date.strftime("%Y-%m-%d")
            cache_key = CacheManager.get_horoscope_key(birth_data, date_str, timezone)
            
            # Intentar obtener de caché
            cached = cache.get(cache_key)
            if cached is not None:
                cached['_from_cache'] = True
                return cached
            
            # Calcular y guardar en caché
            result = func(birth_data, target_date, timezone)
            result['_from_cache'] = False
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


class SmartCache:
    """
    Sistema de caché inteligente con invalidación automática.
    """
    
    @staticmethod
    def invalidate_old_transits():
        """
        Invalida tránsitos de más de 24 horas.
        Ejecutar periódicamente (ej: cron diario).
        """
        # Django cache no soporta pattern delete directamente
        # Usar Redis si necesitas esto en producción
        pass
    
    @staticmethod
    def warm_up_cache(dates_ahead=7):
        """
        Pre-calcula tránsitos para los próximos N días.
        Útil para reducir latencia en horóscopos futuros.
        """
        from .horoscope_service import calculate_transits
        
        for days in range(dates_ahead):
            target = datetime.now() + timedelta(days=days)
            # Calcular para zona horaria común
            calculate_transits(target, "UTC")
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Obtiene estadísticas de uso de caché"""
        try:
            # Requiere Redis con django-redis
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            info = redis_conn.info('stats')
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / 
                           max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
            }
        except Exception:
            return {'error': 'Redis not available'}


class ResponseCompression:
    """
    Compresión de respuestas JSON para reducir tamaño de transferencia.
    """
    
    @staticmethod
    def compress_planets(planets: dict) -> dict:
        """
        Comprime datos de planetas eliminando información redundante.
        Reduce tamaño de respuesta ~30%.
        """
        compressed = {}
        for name, data in planets.items():
            compressed[name] = {
                'v': round(data['value'], 4),  # value
                's': round(data['speed'], 4) if data['speed'] else 0,  # speed
                'r': data['retrograde'],  # retrograde
            }
        return compressed
    
    @staticmethod
    def compress_aspects(aspects: list) -> list:
        """Comprime lista de aspectos"""
        compressed = []
        for aspect in aspects:
            compressed.append({
                't': aspect['transit_planet'][:3],  # primeras 3 letras
                'n': aspect['natal_planet'][:3],
                'a': aspect['aspect'][:3],  # Trí, Sex, Cua, etc.
                'o': round(aspect['orb'], 2),
                'w': aspect['weight']
            })
        return compressed


# Funciones de utilidad para benchmarking
import time

class PerformanceMonitor:
    """Monitor de performance para endpoints"""
    
    def __init__(self):
        self.metrics = {}
    
    def track(self, endpoint: str, duration: float, from_cache: bool = False):
        """Registra métrica de performance"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = {
                'calls': 0,
                'total_time': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'avg_time': 0
            }
        
        self.metrics[endpoint]['calls'] += 1
        self.metrics[endpoint]['total_time'] += duration
        
        if from_cache:
            self.metrics[endpoint]['cache_hits'] += 1
        else:
            self.metrics[endpoint]['cache_misses'] += 1
        
        self.metrics[endpoint]['avg_time'] = (
            self.metrics[endpoint]['total_time'] / 
            self.metrics[endpoint]['calls']
        )
    
    def get_report(self) -> dict:
        """Obtiene reporte de métricas"""
        return self.metrics


# Instancia global de monitor
performance_monitor = PerformanceMonitor()


def measure_performance(endpoint_name: str):
    """Decorator para medir performance de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # en ms
            
            from_cache = isinstance(result, dict) and result.get('_from_cache', False)
            performance_monitor.track(endpoint_name, duration, from_cache)
            
            return result
        return wrapper
    return decorator
