# API de Horóscopo Diario - Documentación

## Nuevos Endpoints

### 1. `/api/horoscope/daily/` - Horóscopo Diario Personalizado

**Método:** `POST`

**Descripción:** Genera horóscopo diario personalizado comparando tránsitos actuales con la carta natal del usuario.

**Payload:**
```json
{
  "birth_data": {
    "planets": { ... },  // Salida completa del endpoint /api/compute/
    "houses": { ... }
  },
  "target_date": "2025-10-09",  // Opcional, default: hoy
  "timezone": "America/Tegucigalpa"  // Opcional, default: UTC
}
```

**Respuesta:**
```json
{
  "date": "2025-10-09",
  "natal_ascendant": "Virgo 19° 44' 40\"",
  "transits": {
    "sun": {
      "longitude": 196.815,
      "speed": 0.983,
      "sign": "Libra",
      "sign_index": 6,
      "degree_in_sign": 16.815
    },
    "moon": {
      "longitude": 54.798,
      "speed": 13.245,
      "sign": "Tauro",
      "sign_index": 1,
      "degree_in_sign": 24.798
    }
    // ... todos los planetas
  },
  "top_aspects": [
    {
      "transit_planet": "moon",
      "natal_planet": "venus",
      "aspect": "Trígono",
      "angle": 124.622,
      "orb": 4.622,
      "applying": true,
      "weight": 15
    }
    // Top 5 aspectos más importantes
  ],
  "houses_activated": [
    {
      "house": 2,
      "weight": 15,
      "planets": [
        {"planet": "mercury", "is_fast": true},
        {"planet": "mars", "is_fast": true}
      ]
    }
    // Top 3 casas más activadas
  ],
  "interpretation": {
    "summary": "**Aspectos clave del día:**\n- Moon en trígono a tu Venus natal: flujo favorable...",
    "advice": "Día favorable para avanzar en tus proyectos. Mantén el foco y confía en el flujo."
  }
}
```

---

### 2. `/api/transits/` - Posiciones Planetarias del Día

**Método:** `GET`

**Descripción:** Retorna posiciones planetarias (tránsitos) para una fecha específica.

**Parámetros de Query:**
- `date`: Fecha en formato YYYY-MM-DD (opcional, default: hoy)
- `timezone`: Zona horaria (opcional, default: UTC)

**Ejemplo:**
```
GET /api/transits/?date=2025-10-09&timezone=America/Tegucigalpa
```

**Respuesta:**
```json
{
  "date": "2025-10-09",
  "timezone": "America/Tegucigalpa",
  "transits": {
    "sun": {
      "longitude": 196.815,
      "speed": 0.983,
      "sign": "Libra",
      "sign_index": 6,
      "degree_in_sign": 16.815
    },
    "moon": {
      "longitude": 54.798,
      "speed": 13.245,
      "sign": "Tauro",
      "sign_index": 1,
      "degree_in_sign": 24.798
    }
    // ... todos los planetas
  }
}
```

---

## Flujo de Uso Completo

### Paso 1: Calcular Carta Natal (una vez)

```bash
curl -X POST http://localhost:8000/api/compute/ \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "1992-12-07T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "P",
    "topocentric_moon_only": false
  }'
```

**Guardar esta respuesta** como `natal_chart.json` en tu aplicación/base de datos.

---

### Paso 2: Consultar Horóscopo Diario (cada día)

```bash
curl -X POST http://localhost:8000/api/horoscope/daily/ \
  -H "Content-Type: application/json" \
  -d '{
    "birth_data": {
      "planets": { ... },  // Del natal_chart.json
      "houses": { ... }
    },
    "target_date": "2025-10-09",
    "timezone": "America/Tegucigalpa"
  }'
```

---

## Interpretación de Resultados

### Aspectos

- **Conjunción (0°):** Fusión de energías, inicio de ciclo
- **Sextil (60°):** Oportunidad, requiere acción
- **Cuadratura (90°):** Tensión creativa, desafío
- **Trígono (120°):** Flujo natural, facilidad
- **Oposición (180°):** Polaridad, necesidad de balance

### Peso de Aspectos

- **Planetas rápidos** (Luna, Mercurio, Venus, Marte): Mayor impacto en lo diario
- **Planetas lentos** (Júpiter, Saturno, Urano, Neptuno, Pluto): Tendencias más largas
- **Aplicativo**: Aspecto formándose (más fuerte)
- **Separativo**: Aspecto disolviéndose (menos intenso)

### Casas Activadas

Indica qué áreas de vida están siendo estimuladas por los tránsitos:

1. **Casa 1:** Identidad, cuerpo, iniciativa
2. **Casa 2:** Dinero, recursos, valores
3. **Casa 3:** Comunicación, estudios cortos, hermanos
4. **Casa 4:** Hogar, familia, raíces
5. **Casa 5:** Amor, creatividad, hijos
6. **Casa 6:** Trabajo diario, salud, rutinas
7. **Casa 7:** Pareja, asociaciones, contratos
8. **Casa 8:** Transformación, sexualidad, finanzas compartidas
9. **Casa 9:** Viajes, estudios superiores, filosofía
10. **Casa 10:** Carrera, reputación, vocación
11. **Casa 11:** Amistades, grupos, proyectos colectivos
12. **Casa 12:** Espiritualidad, descanso, inconsciente

---

## Configuración de Orbes

Los orbes (margen de grados) están optimizados para horóscopos diarios:

| Aspecto | Planetas Rápidos | Planetas Lentos |
|---------|------------------|-----------------|
| Conjunción | 8° | 6° |
| Sextil | 6° | 4° |
| Cuadratura | 7° | 5° |
| Trígono | 8° | 6° |
| Oposición | 8° | 6° |

---

## Algoritmo de Selección

1. **Calcular todos los aspectos** entre tránsitos y posiciones natales
2. **Asignar peso** según:
   - Velocidad del planeta (rápido > lento)
   - Tipo de aspecto (armónico > tenso)
   - Exactitud del aspecto (orbe pequeño > grande)
   - Si es aplicativo o separativo
3. **Seleccionar top 5 aspectos** más importantes
4. **Identificar casas activadas** por tránsitos rápidos
5. **Generar interpretación** personalizada

---

## Ejemplo de Integración en Python

```python
import requests
from datetime import datetime

# 1. Obtener carta natal (hacer una vez)
birth_data = {
    "datetime": "1992-12-07T23:58:00",
    "timezone": "America/Tegucigalpa",
    "latitude": 14.0723,
    "longitude": -87.1921,
    "house_system": "P",
    "topocentric_moon_only": False
}

response = requests.post(
    "http://localhost:8000/api/compute/",
    json=birth_data
)
natal_chart = response.json()

# 2. Obtener horóscopo diario
horoscope_payload = {
    "birth_data": {
        "planets": natal_chart["planets"],
        "houses": natal_chart["houses"]
    },
    "target_date": datetime.now().strftime("%Y-%m-%d"),
    "timezone": "America/Tegucigalpa"
}

response = requests.post(
    "http://localhost:8000/api/horoscope/daily/",
    json=horoscope_payload
)
daily_horoscope = response.json()

# 3. Mostrar interpretación
print(daily_horoscope["interpretation"]["summary"])
print("\nConsejo del día:")
print(daily_horoscope["interpretation"]["advice"])
```

---

## Notas Técnicas

### Precisión de Cálculos

- Usa Swiss Ephemeris (misma precisión que Astro.com)
- Tránsitos calculados para hora exacta especificada
- Aspectos calculados con longitud eclíptica geocéntrica

### Performance

- **Tránsitos:** ~50ms (solo posiciones planetarias)
- **Horóscopo completo:** ~200ms (incluyendo aspectos y análisis)

### Límites

- Máximo 5 aspectos top mostrados
- Máximo 3 casas más activadas
- Orbes configurables en `horoscope_service.py`

---

## Próximas Mejoras

- [ ] Sistema de plantillas más rico por combinación planeta-planeta
- [ ] Intensidad lunar (días de Luna Llena, Nueva, etc.)
- [ ] Retrogradaciones de planetas en tránsito
- [ ] Aspectos múltiples (T-Cuadradas, Grandes Trígonos)
- [ ] Puntos arábigos en tránsito
- [ ] Configuración personalizada de orbes por usuario
