# Tránsitos Lunares y Eclipses - Guía de API

Esta guía explica cómo obtener información sobre tránsitos lunares diarios y eclipses solares/lunares mensuales usando la API de AstroAPI.

## 1. Tránsitos Lunares Diarios

### Endpoint
```
GET /api/transits/
```

### Parámetros de consulta
- `date` (opcional): Fecha en formato YYYY-MM-DD. Si no se especifica, usa la fecha actual.
- `timezone` (opcional): Zona horaria (ej: "America/Tegucigalpa"). Por defecto: "UTC".

### Ejemplo de petición
```bash
# Para la fecha actual
curl -X GET "http://localhost:8000/api/transits/"

# Para una fecha específica
curl -X GET "http://localhost:8000/api/transits/?date=2025-10-17&timezone=America/Tegucigalpa"
```

### Respuesta
La API devuelve la posición actual de la Luna en el zodíaco.

```json
{
  "date": "2025-10-17",
  "timezone": "America/Tegucigalpa",
  "transits": {
    "moon": {
      "longitude": 123.45,
      "speed": 12.34,
      "sign": "Leo",
      "sign_index": 4,
      "degree_in_sign": 3.45
    }
  }
}
```

**Campos de respuesta:**
- `longitude`: Longitud zodiacal en grados (0-360°)
- `speed`: Velocidad de movimiento en grados/día
- `sign`: Signo zodiacal en español
- `sign_index`: Índice del signo (0=Aries, 1=Tauro, etc.)
- `degree_in_sign`: Grados dentro del signo (0-29.99°)

## 2. Tránsitos Lunares Mensuales y Eclipses

### Endpoint
```
GET /api/monthly-transits/{month}/{year}/
```

### Parámetros de URL
- `month`: Mes (1-12)
- `year`: Año (1900-2100)

### Ejemplo de petición
```bash
# Tránsitos y eclipses de octubre 2025
curl -X GET "http://localhost:8000/api/monthly-transits/10/2025/"
```

### Respuesta
Devuelve una lista de tránsitos importantes del mes que involucran a la Luna, incluyendo eclipses solares y lunares.

```json
{
  "month": 10,
  "year": 2025,
  "important_transits": [
    {
      "date": "2025-10-14",
      "aspect": "Eclipse Solar",
      "planets": ["Sol", "Luna"],
      "angle": 0.5,
      "is_eclipse": true
    },
    {
      "date": "2025-10-20",
      "aspect": "Cuadratura",
      "planets": ["Luna", "Marte"],
      "angle": 89.8,
      "is_eclipse": false
    },
    {
      "date": "2025-10-28",
      "aspect": "Eclipse Lunar",
      "planets": ["Sol", "Luna"],
      "angle": 179.2,
      "is_eclipse": true
    }
  ]
}
```

**Campos de respuesta:**
- `date`: Fecha del tránsito
- `aspect`: Tipo de aspecto ("Eclipse Solar", "Eclipse Lunar", "Conjunción", "Oposición", "Cuadratura", etc.)
- `planets`: Planetas involucrados (siempre incluye "Luna")
- `angle`: Ángulo exacto del aspecto en grados
- `is_eclipse`: `true` si es un eclipse, `false` si es un tránsito lunar normal

## Notas importantes

1. **Eclipses**: Se detectan automáticamente cuando la Luna está en conjunción/oposición con el Sol y cerca del Nodo Lunar (dentro de 15°).

2. **Zona horaria**: Para tránsitos diarios, afecta la conversión de fecha local a UTC para cálculos astronómicos precisos.

3. **Precisión**: Los cálculos usan ephemeris Swiss Ephemeris DE431 para máxima precisión astronómica.

4. **Caché**: Las respuestas se cachean para mejorar rendimiento (1 hora para tránsitos diarios).

5. **Errores**: Si hay un error, la respuesta incluirá un campo `error` con la descripción del problema.

## Ejemplos prácticos

### Obtener tránsito lunar de hoy
```bash
curl -X GET "http://localhost:8000/api/transits/" | jq .
```

### Buscar eclipses en noviembre 2025
```bash
curl -X GET "http://localhost:8000/api/monthly-transits/11/2025/" | jq .
```

### Verificar si hay eclipse lunar hoy
```bash
curl -X GET "http://localhost:8000/api/transits/?date=$(date +%Y-%m-%d)" | jq .
```</content>
<parameter name="filePath">c:\Users\hecto\Desktop\escritorio\astroapi\TRANSITOS_LUNARES_ECLIPSES.md