"""
Script de benchmark para medir mejoras de performance con caché.
Compara velocidad con y sin caché.
"""

import requests
import time
from statistics import mean, median
import json

API_URL = "http://localhost:8000/api"

# Datos de prueba (Tegucigalpa)
BIRTH_DATA = {
    "datetime": "1992-12-07T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "P",
    "topocentric_moon_only": False
}


def benchmark_endpoint(url, method="GET", payload=None, iterations=10):
    """Mide tiempo de respuesta de un endpoint"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        duration = (time.time() - start) * 1000  # ms
        times.append(duration)
        
        # Verificar éxito
        if response.status_code not in [200, 201]:
            print(f"❌ Error: {response.status_code} - {response.text[:100]}")
            return None
        
        # Pequeña pausa entre requests
        if i < iterations - 1:
            time.sleep(0.1)
    
    return {
        "times": times,
        "mean": mean(times),
        "median": median(times),
        "min": min(times),
        "max": max(times),
        "total": sum(times)
    }


def print_benchmark_results(name, results):
    """Imprime resultados formateados"""
    if not results:
        print(f"\n❌ {name}: FAILED")
        return
    
    print(f"\n📊 {name}")
    print(f"   Promedio: {results['mean']:.2f}ms")
    print(f"   Mediana:  {results['median']:.2f}ms")
    print(f"   Mínimo:   {results['min']:.2f}ms")
    print(f"   Máximo:   {results['max']:.2f}ms")
    print(f"   Total:    {results['total']:.2f}ms")


def main():
    print("="*80)
    print("🚀 BENCHMARK DE PERFORMANCE - ASTRO API")
    print("="*80)
    
    # 1. Health Check (baseline)
    print("\n1️⃣  Health Check (baseline)")
    results = benchmark_endpoint(f"{API_URL}/health/", iterations=20)
    print_benchmark_results("Health Check", results)
    
    # 2. Tránsitos del día (se beneficia de caché)
    print("\n2️⃣  Tránsitos del Día")
    print("   Primera ejecución (sin caché)...")
    results_cold = benchmark_endpoint(
        f"{API_URL}/transits/?date=2025-10-09&timezone=America/Tegucigalpa",
        iterations=1
    )
    
    print("   Ejecuciones subsecuentes (con caché)...")
    results_warm = benchmark_endpoint(
        f"{API_URL}/transits/?date=2025-10-09&timezone=America/Tegucigalpa",
        iterations=10
    )
    
    if results_cold and results_warm:
        print(f"\n   ⚡ Sin caché: {results_cold['mean']:.2f}ms")
        print(f"   ⚡ Con caché: {results_warm['mean']:.2f}ms")
        improvement = ((results_cold['mean'] - results_warm['mean']) / results_cold['mean']) * 100
        print(f"   📈 Mejora: {improvement:.1f}% más rápido")
    
    # 3. Carta Natal
    print("\n3️⃣  Carta Natal (Compute)")
    print("   Primera ejecución...")
    results_natal = benchmark_endpoint(
        f"{API_URL}/compute/",
        method="POST",
        payload=BIRTH_DATA,
        iterations=1
    )
    
    print("   Ejecuciones subsecuentes (con caché)...")
    results_natal_cached = benchmark_endpoint(
        f"{API_URL}/compute/",
        method="POST",
        payload=BIRTH_DATA,
        iterations=5
    )
    
    if results_natal and results_natal_cached:
        print(f"\n   ⚡ Sin caché: {results_natal['mean']:.2f}ms")
        print(f"   ⚡ Con caché: {results_natal_cached['mean']:.2f}ms")
        improvement = ((results_natal['mean'] - results_natal_cached['mean']) / results_natal['mean']) * 100
        print(f"   📈 Mejora: {improvement:.1f}% más rápido")
    
    # 4. Horóscopo Diario (endpoint más complejo)
    print("\n4️⃣  Horóscopo Diario")
    
    # Primero obtener carta natal
    print("   Obteniendo carta natal...")
    natal_response = requests.post(f"{API_URL}/compute/", json=BIRTH_DATA)
    natal_chart = natal_response.json()
    
    horoscope_payload = {
        "birth_data": {
            "planets": natal_chart["planets"],
            "houses": natal_chart["houses"]
        },
        "timezone": "America/Tegucigalpa"
    }
    
    print("   Primera ejecución (sin caché)...")
    results_horoscope_cold = benchmark_endpoint(
        f"{API_URL}/horoscope/daily/",
        method="POST",
        payload=horoscope_payload,
        iterations=1
    )
    
    print("   Ejecuciones subsecuentes (con caché)...")
    results_horoscope_warm = benchmark_endpoint(
        f"{API_URL}/horoscope/daily/",
        method="POST",
        payload=horoscope_payload,
        iterations=10
    )
    
    if results_horoscope_cold and results_horoscope_warm:
        print(f"\n   ⚡ Sin caché: {results_horoscope_cold['mean']:.2f}ms")
        print(f"   ⚡ Con caché: {results_horoscope_warm['mean']:.2f}ms")
        improvement = ((results_horoscope_cold['mean'] - results_horoscope_warm['mean']) / results_horoscope_cold['mean']) * 100
        print(f"   📈 Mejora: {improvement:.1f}% más rápido")
    
    # 5. Estadísticas de caché
    print("\n5️⃣  Estadísticas de Caché")
    try:
        stats_response = requests.get(f"{API_URL}/cache/stats/")
        stats = stats_response.json()
        
        print("\n   Performance Metrics:")
        for endpoint, metrics in stats.get("performance", {}).items():
            print(f"   • {endpoint}:")
            print(f"     - Llamadas: {metrics['calls']}")
            print(f"     - Tiempo promedio: {metrics['avg_time']:.2f}ms")
            print(f"     - Cache hits: {metrics['cache_hits']}")
            print(f"     - Cache misses: {metrics['cache_misses']}")
            if metrics['calls'] > 0:
                hit_rate = (metrics['cache_hits'] / metrics['calls']) * 100
                print(f"     - Hit rate: {hit_rate:.1f}%")
    
    except Exception as e:
        print(f"   ⚠️  No se pudieron obtener estadísticas: {e}")
    
    # Resumen final
    print("\n" + "="*80)
    print("📈 RESUMEN DE MEJORAS")
    print("="*80)
    
    improvements = []
    
    if results_cold and results_warm:
        transit_improvement = ((results_cold['mean'] - results_warm['mean']) / results_cold['mean']) * 100
        improvements.append(("Tránsitos", transit_improvement, results_cold['mean'], results_warm['mean']))
    
    if results_natal and results_natal_cached:
        natal_improvement = ((results_natal['mean'] - results_natal_cached['mean']) / results_natal['mean']) * 100
        improvements.append(("Carta Natal", natal_improvement, results_natal['mean'], results_natal_cached['mean']))
    
    if results_horoscope_cold and results_horoscope_warm:
        horoscope_improvement = ((results_horoscope_cold['mean'] - results_horoscope_warm['mean']) / results_horoscope_cold['mean']) * 100
        improvements.append(("Horóscopo", horoscope_improvement, results_horoscope_cold['mean'], results_horoscope_warm['mean']))
    
    for name, improvement, cold, warm in improvements:
        print(f"\n✅ {name}:")
        print(f"   Sin caché: {cold:.2f}ms → Con caché: {warm:.2f}ms")
        print(f"   Mejora: {improvement:.1f}% más rápido ({cold - warm:.2f}ms ahorrados)")
    
    if improvements:
        avg_improvement = mean([imp for _, imp, _, _ in improvements])
        print(f"\n🎯 Mejora promedio: {avg_improvement:.1f}%")
        
        total_cold = sum([cold for _, _, cold, _ in improvements])
        total_warm = sum([warm for _, _, _, warm in improvements])
        total_saved = total_cold - total_warm
        
        print(f"   Tiempo total sin caché: {total_cold:.2f}ms")
        print(f"   Tiempo total con caché: {total_warm:.2f}ms")
        print(f"   Tiempo ahorrado: {total_saved:.2f}ms")
    
    print("\n" + "="*80)
    print("✅ Benchmark completado!")
    print("="*80)


if __name__ == "__main__":
    try:
        # Verificar que el servidor esté corriendo
        response = requests.get(f"{API_URL}/health/", timeout=5)
        if response.status_code != 200:
            print("❌ Error: El servidor no está respondiendo correctamente")
            print(f"   URL: {API_URL}")
            exit(1)
        
        main()
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print(f"   Asegúrate de que el servidor esté corriendo en {API_URL}")
        print("   Ejecuta: cd backend && python manage.py runserver")
        exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrumpido por el usuario")
        exit(0)
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
