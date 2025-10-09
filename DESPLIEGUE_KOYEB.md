# 🚀 Despliegue a Koyeb con Horóscopo Diario

## Cambios para Producción

### 1. Variables de Entorno (NO cambiar)
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=tu_clave_segura_unica
DJANGO_ALLOWED_HOSTS=*
SOURCE_REPO_URL=https://github.com/hectorherrerafullstack/astroApi
```

### 2. Comando de Inicio (Actualizado)
```bash
cd backend && gunicorn backend.wsgi --bind 0.0.0.0:$PORT
```

### 3. Endpoints Disponibles
```
GET  /api/health/
POST /api/compute/
POST /api/horoscope/daily/
GET  /api/transits/
```

---

## 🧪 Testing en Producción

### 1. Health Check
```bash
curl https://tu-app.koyeb.app/api/health/
# Respuesta: {"status": "ok"}
```

### 2. Calcular Carta Natal
```bash
curl -X POST https://tu-app.koyeb.app/api/compute/ \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1992-12-07T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "P",
    "topocentric_moon_only": false
  }' | jq '.planets | keys'
```

### 3. Horóscopo Diario
```bash
# Primero obtén la carta natal y guárdala en natal.json
curl -X POST https://tu-app.koyeb.app/api/compute/ \
  -H "Content-Type: application/json" \
  -d '{...}' > natal.json

# Luego obtén el horóscopo del día
curl -X POST https://tu-app.koyeb.app/api/horoscope/daily/ \
  -H "Content-Type: application/json" \
  -d "{
    \"birth_data\": $(cat natal.json | jq '{planets, houses}'),
    \"timezone\": \"America/Tegucigalpa\"
  }" | jq '.interpretation.advice'
```

### 4. Tránsitos Simples
```bash
curl "https://tu-app.koyeb.app/api/transits/?date=2025-10-09&timezone=America/Tegucigalpa" | jq '.transits'
```

---

## 📊 Monitoreo

### Logs a Revisar
```bash
# En Koyeb Dashboard > Logs
grep "POST /api/horoscope/daily/" app.log
grep "GET /api/transits/" app.log
grep "ERROR" app.log
```

### Métricas Clave
- **Latencia `/api/horoscope/daily/`**: < 300ms esperado
- **Latencia `/api/transits/`**: < 100ms esperado
- **Tasa de error**: < 1%

---

## 🔧 Troubleshooting

### Error: "SwissEph file not found"
**Problema:** Archivos de efemérides no encontrados  
**Solución:** Verificar que `se_data/` esté en el contenedor
```bash
# En Koyeb: Add persistent volume
# Mount path: /app/se_data
# Upload all *.se1 files
```

### Error: "Missing 'birth_data' field"
**Problema:** Payload incorrecto en `/api/horoscope/daily/`  
**Solución:** Asegurar que birth_data contiene `planets` y `houses`
```json
{
  "birth_data": {
    "planets": {...},  // Requerido
    "houses": {...}    // Requerido
  }
}
```

### Error: "Invalid date format"
**Problema:** Formato de fecha incorrecto  
**Solución:** Usar formato ISO `YYYY-MM-DD`
```bash
# Correcto
"target_date": "2025-10-09"

# Incorrecto
"target_date": "09/10/2025"
"target_date": "2025-10-09T00:00:00"
```

---

## 🎯 Checklist de Despliegue

### Pre-Deploy
- [ ] Código pusheado a GitHub con último commit
- [ ] Variables de entorno configuradas en Koyeb
- [ ] `se_data/` montado como volumen persistente
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `cd backend && gunicorn backend.wsgi --bind 0.0.0.0:$PORT`

### Post-Deploy
- [ ] Health check responde correctamente
- [ ] `/api/compute/` calcula carta natal sin errores
- [ ] `/api/horoscope/daily/` retorna horóscopo con interpretación
- [ ] `/api/transits/` retorna posiciones planetarias
- [ ] Headers AGPL (`X-License`, `X-Source-Code`) presentes
- [ ] Logs no muestran errores críticos

### Validación Completa
```bash
# Script de validación completo
./validate_production.sh https://tu-app.koyeb.app
```

---

## 📈 Optimizaciones para Producción

### 1. Rate Limiting (Recomendado)
```python
# Agregar a backend/backend/settings.py
INSTALLED_APPS += ['django_ratelimit']

# En views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def daily_horoscope_view(request):
    ...
```

### 2. Caché de Tránsitos
```python
# Los tránsitos son iguales para todos en la misma fecha/hora
# Implementar caché con Redis o Django cache

from django.core.cache import cache

def calculate_transits(dt, timezone):
    cache_key = f"transits_{dt.date()}_{timezone}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    transits = _calculate_transits_raw(dt, timezone)
    cache.set(cache_key, transits, timeout=3600)  # 1 hora
    return transits
```

### 3. Async Processing para Batch
```python
# Para múltiples usuarios, usar Celery
from celery import shared_task

@shared_task
def generate_daily_horoscopes_batch(user_ids):
    for user_id in user_ids:
        natal_chart = db.get_natal_chart(user_id)
        horoscope = generate_daily_horoscope_personal(natal_chart)
        db.save_horoscope(user_id, horoscope)
```

---

## 🌐 Integración con Frontend

### React/Next.js Example
```javascript
// hooks/useHoroscope.js
import { useState, useEffect } from 'react';

export function useHoroscope(natalChart) {
  const [horoscope, setHoroscope] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHoroscope() {
      const response = await fetch('/api/horoscope/daily/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          birth_data: {
            planets: natalChart.planets,
            houses: natalChart.houses
          },
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
      });
      const data = await response.json();
      setHoroscope(data);
      setLoading(false);
    }
    fetchHoroscope();
  }, [natalChart]);

  return { horoscope, loading };
}
```

### Vue.js Example
```javascript
// composables/useHoroscope.js
import { ref, onMounted } from 'vue';

export function useHoroscope(natalChart) {
  const horoscope = ref(null);
  const loading = ref(true);

  onMounted(async () => {
    const response = await fetch('/api/horoscope/daily/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        birth_data: {
          planets: natalChart.planets,
          houses: natalChart.houses
        }
      })
    });
    horoscope.value = await response.json();
    loading.value = false;
  });

  return { horoscope, loading };
}
```

---

## 📱 Notificaciones Push

### Firebase Cloud Messaging Integration
```python
# backend/api/notifications.py
from firebase_admin import messaging

def send_daily_horoscope_notification(user_token, horoscope):
    message = messaging.Message(
        notification=messaging.Notification(
            title="🌟 Tu Horóscopo del Día",
            body=horoscope['interpretation']['advice']
        ),
        data={
            'top_aspect': horoscope['top_aspects'][0]['aspect'],
            'date': horoscope['date']
        },
        token=user_token
    )
    messaging.send(message)
```

### Cron Job (Envío Diario)
```python
# Agregar a crontab o usar Celery Beat
# Cada día a las 6 AM
0 6 * * * python manage.py send_daily_horoscopes
```

---

## 💾 Base de Datos para Usuarios

### Schema Recomendado
```sql
-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de cartas natales
CREATE TABLE natal_charts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    planets JSONB NOT NULL,
    houses JSONB NOT NULL,
    birth_datetime TIMESTAMP NOT NULL,
    birth_timezone VARCHAR(50) NOT NULL,
    birth_latitude DECIMAL(9,6) NOT NULL,
    birth_longitude DECIMAL(9,6) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de horóscopos (caché histórico)
CREATE TABLE daily_horoscopes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    horoscope_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Índices para performance
CREATE INDEX idx_natal_charts_user ON natal_charts(user_id);
CREATE INDEX idx_horoscopes_user_date ON daily_horoscopes(user_id, date);
```

---

## 🔐 Autenticación (Si necesitas)

### JWT con Django REST Framework
```python
# settings.py
INSTALLED_APPS += ['rest_framework', 'rest_framework_simplejwt']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def daily_horoscope_view(request):
    user = request.user
    natal_chart = NatalChart.objects.get(user=user)
    ...
```

---

## ✅ Validación Final

### Script de Validación Automática
```bash
#!/bin/bash
# validate_production.sh

API_URL=$1

echo "🔍 Validando API en $API_URL"

# Test 1: Health Check
echo "Test 1: Health Check"
curl -s "$API_URL/api/health/" | jq '.status'

# Test 2: Compute
echo "Test 2: Compute Chart"
NATAL=$(curl -s -X POST "$API_URL/api/compute/" \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1992-12-07T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "P",
    "topocentric_moon_only": false
  }')
echo $NATAL | jq '.planets | keys | length'

# Test 3: Daily Horoscope
echo "Test 3: Daily Horoscope"
curl -s -X POST "$API_URL/api/horoscope/daily/" \
  -H "Content-Type: application/json" \
  -d "{
    \"birth_data\": $(echo $NATAL | jq '{planets, houses}')
  }" | jq '.interpretation.advice'

# Test 4: Transits
echo "Test 4: Transits"
curl -s "$API_URL/api/transits/" | jq '.transits | keys | length'

echo "✅ Validación completada"
```

---

## 🎉 ¡Listo para Producción!

Tu API ahora incluye:
- ✅ Cálculo de cartas natales (Swiss Ephemeris)
- ✅ Horóscopo diario personalizado
- ✅ Tránsitos planetarios
- ✅ Interpretación automática
- ✅ Sistema de aspectos completo
- ✅ Análisis de casas activadas
- ✅ Documentación exhaustiva
- ✅ Ejemplos de integración
- ✅ AGPL compliance

**URL del Repositorio:**  
https://github.com/hectorherrerafullstack/astroApi

**Última actualización:** 2025-10-09
