# Posición Lunar Diaria y Mensual - Guía de API

Esta guía explica cómo obtener la posición de la Luna (signo, fase) diaria y mensual usando la API de AstroAPI.

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
  "longitude": 156.45,
  "speed": 12.34,
  "sign": "Virgo",
  "sign_index": 5,
  "degree_in_sign": 6.45,
  "phase": "Creciente Gibosa",
  "phase_angle": 135.67
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

## 2. Posición Lunar Mensual

### Endpoint
```
GET /api/monthly-transits/{month}/{year}/
```

### Parámetros de URL
- `month`: Mes (1-12)
- `year`: Año (1900-2100)

### Ejemplo de petición
```bash
# Posición lunar de octubre 2025
curl -X GET "http://localhost:8000/api/monthly-transits/10/2025/"
```

### Respuesta
Devuelve la posición de la Luna para cada día del mes.

```json
{
  "month": 10,
  "year": 2025,
  "daily_moon": [
    {
      "date": "2025-10-01",
      "longitude": 156.45,
      "speed": 12.34,
      "sign": "Virgo",
      "sign_index": 5,
      "degree_in_sign": 6.45,
      "phase": "Creciente Gibosa",
      "phase_angle": 135.67
    },
    {
      "date": "2025-10-02",
      "longitude": 167.12,
      "speed": 12.56,
      "sign": "Virgo",
      "sign_index": 5,
      "degree_in_sign": 17.12,
      "phase": "Creciente Gibosa",
      "phase_angle": 146.34
    }
  ]
}
```

**Campos de respuesta:**
- `date`: Fecha del día
- `longitude`: Longitud eclíptica de la Luna en grados
- `speed`: Velocidad de la Luna en grados/día
- `sign`: Signo zodiacal en español
- `sign_index`: Índice del signo (0-11)
- `degree_in_sign`: Grados dentro del signo
- `phase`: Fase lunar en español
- `phase_angle`: Ángulo de separación con el Sol en grados (0-360°)

## Notas importantes

1. **Zona horaria**: Para tránsitos diarios, afecta la conversión de fecha local a UTC para cálculos astronómicos precisos.

2. **Precisión**: Los cálculos usan ephemeris Swiss Ephemeris DE431 para máxima precisión astronómica.

3. **Caché**: Las respuestas se cachean para mejorar rendimiento (1 hora para tránsitos diarios).

4. **Errores**: Si hay un error, la respuesta incluirá un campo `error` con la descripción del problema.

## Ejemplos prácticos

### Obtener tránsito lunar de hoy
```bash
curl -X GET "http://localhost:8000/api/transits/" | jq .
```

### Obtener posición lunar mensual
```bash
curl -X GET "http://localhost:8000/api/monthly-transits/11/2025/" | jq .
```

### Verificar posición lunar hoy
```bash
curl -X GET "http://localhost:8000/api/transits/?date=$(date +%Y-%m-%d)" | jq .
```</content>
<parameter name="filePath">c:\Users\hecto\Desktop\escritorio\astroapi\TRANSITOS_LUNARES_ECLIPSES.md