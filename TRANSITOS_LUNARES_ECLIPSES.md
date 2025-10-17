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
La API devuelve la posición actual de la Luna en el zodíaco, incluyendo su fase lunar.

```json
{
  "date": "2025-10-17",
  "timezone": "America/Tegucigalpa",
  "transits": {
    "moon": {
      "longitude": 156.45,
      "speed": 12.34,
      "sign": "Virgo",
      "sign_index": 5,
      "degree_in_sign": 6.45,
      "phase": "Creciente Gibosa",
      "phase_angle": 135.67
    }
  }
}
```

**Campos adicionales para la Luna:**
- `phase`: Nombre de la fase lunar en español
- `phase_angle`: Ángulo de separación con el Sol en grados (0-360°)

**Fases lunares:**
- Luna Nueva (0-45°)
- Creciente Menguante (45-90°)
- Cuarto Creciente (90-135°)
- Creciente Gibosa (135-180°)
- Luna Llena (180-225°)
- Menguante Gibosa (225-270°)
- Cuarto Menguante (270-315°)
- Menguante Creciente (315-360°)

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

1. **Eclipses**: Se detectan automáticamente cuando la Luna Nueva o Llena ocurre cerca de los Nodos Lunares (Nodo Norte o Nodo Sur).
   
   **🌑 Eclipse Solar (Luna Nueva cerca de los nodos):**
   - Ocurre cuando el Sol y la Luna están en conjunción dentro de 15° de distancia del Nodo Lunar.
   - Si están más cerca (dentro de 10° o menos), el eclipse es total o anular.
   - Si están más lejos (hasta 15°), se considera parcial o penumbral.
   
   **🌕 Eclipse Lunar (Luna Llena cerca de los nodos):**
   - Se da cuando el Sol y la Luna están en oposición y el eje de esa oposición cae a menos de 12-15° de los nodos.
   - Cuanto más cerca del nodo esté la Luna llena, más exacto y potente será el eclipse.

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