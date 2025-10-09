# Ejemplos de Uso con CURL - API de Horóscopo Diario

## Requisitos
- API corriendo en `http://localhost:8000` (o tu URL de producción)
- `curl` instalado
- `jq` (opcional, para formatear JSON)

---

## 1. Health Check

Verificar que la API está funcionando:

```bash
curl http://localhost:8000/api/health/
```

**Respuesta:**
```json
{"status": "ok"}
```

---

## 2. Calcular Carta Natal

**Paso 1:** Calcular la carta natal (hacer **una sola vez** por usuario):

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

**Guardar la respuesta** en `natal_chart.json`:

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
  }' > natal_chart.json
```

---

## 3. Horóscopo del Día

**Paso 2:** Obtener horóscopo diario (usar cada día):

```bash
curl -X POST http://localhost:8000/api/horoscope/daily/ \
  -H "Content-Type: application/json" \
  -d @horoscopo_payload.json
```

Donde `horoscopo_payload.json` contiene:

```json
{
  "birth_data": {
    "planets": { 
      ... (copiar desde natal_chart.json) 
    },
    "houses": { 
      ... (copiar desde natal_chart.json) 
    }
  },
  "timezone": "America/Tegucigalpa"
}
```

### Horóscopo para fecha específica:

```bash
curl -X POST http://localhost:8000/api/horoscope/daily/ \
  -H "Content-Type: application/json" \
  -d '{
    "birth_data": {
      "planets": {...},
      "houses": {...}
    },
    "target_date": "2025-10-15",
    "timezone": "America/Tegucigalpa"
  }'
```

---

## 4. Solo Tránsitos (sin carta natal)

Obtener posiciones planetarias actuales:

```bash
curl "http://localhost:8000/api/transits/?timezone=America/Tegucigalpa"
```

### Tránsitos para fecha específica:

```bash
curl "http://localhost:8000/api/transits/?date=2025-10-15&timezone=America/Tegucigalpa"
```

---

## 5. Script Completo - Bash

Guardar como `horoscopo.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000/api"
TIMEZONE="America/Tegucigalpa"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Horóscopo Diario ===${NC}\n"

# 1. Verificar si existe carta natal
if [ ! -f "natal_chart.json" ]; then
    echo -e "${GREEN}Calculando carta natal...${NC}"
    curl -s -X POST "$API_URL/compute/" \
      -H "Content-Type: application/json" \
      -d '{
        "datetime": "1992-12-07T23:58:00",
        "timezone": "'"$TIMEZONE"'",
        "latitude": 14.0723,
        "longitude": -87.1921,
        "house_system": "P",
        "topocentric_moon_only": false
      }' > natal_chart.json
    echo -e "${GREEN}✓ Carta natal guardada${NC}\n"
fi

# 2. Construir payload para horóscopo
PLANETS=$(jq -c '.planets' natal_chart.json)
HOUSES=$(jq -c '.houses' natal_chart.json)

PAYLOAD=$(cat <<EOF
{
  "birth_data": {
    "planets": $PLANETS,
    "houses": $HOUSES
  },
  "timezone": "$TIMEZONE"
}
EOF
)

# 3. Obtener horóscopo del día
echo -e "${GREEN}Obteniendo horóscopo del día...${NC}"
HOROSCOPE=$(curl -s -X POST "$API_URL/horoscope/daily/" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# 4. Mostrar resultado
echo -e "\n${BLUE}Fecha:${NC} $(echo $HOROSCOPE | jq -r '.date')"
echo -e "${BLUE}Ascendente:${NC} $(echo $HOROSCOPE | jq -r '.natal_ascendant')"

echo -e "\n${BLUE}Top 3 Aspectos:${NC}"
echo $HOROSCOPE | jq -r '.top_aspects[:3][] | "  • \(.transit_planet | ascii_upcase) \(.aspect) \(.natal_planet | ascii_upcase) (orbe: \(.orb)°)"'

echo -e "\n${BLUE}Consejo del día:${NC}"
echo $HOROSCOPE | jq -r '.interpretation.advice'

# 5. Guardar horóscopo completo
echo $HOROSCOPE | jq '.' > "horoscope_$(date +%Y-%m-%d).json"
echo -e "\n${GREEN}✓ Horóscopo guardado en horoscope_$(date +%Y-%m-%d).json${NC}"
```

Ejecutar:
```bash
chmod +x horoscopo.sh
./horoscopo.sh
```

---

## 6. Script Completo - PowerShell

Guardar como `horoscopo.ps1`:

```powershell
# Configuración
$API_URL = "http://localhost:8000/api"
$TIMEZONE = "America/Tegucigalpa"

Write-Host "`n=== Horóscopo Diario ===`n" -ForegroundColor Blue

# 1. Verificar si existe carta natal
if (-not (Test-Path "natal_chart.json")) {
    Write-Host "Calculando carta natal..." -ForegroundColor Green
    
    $birthData = @{
        datetime = "1992-12-07T23:58:00"
        timezone = $TIMEZONE
        latitude = 14.0723
        longitude = -87.1921
        house_system = "P"
        topocentric_moon_only = $false
    } | ConvertTo-Json
    
    $natalChart = Invoke-RestMethod -Uri "$API_URL/compute/" -Method Post `
        -ContentType "application/json" -Body $birthData
    
    $natalChart | ConvertTo-Json -Depth 100 | Out-File "natal_chart.json"
    Write-Host "✓ Carta natal guardada`n" -ForegroundColor Green
}

# 2. Cargar carta natal
$natalChart = Get-Content "natal_chart.json" | ConvertFrom-Json

# 3. Construir payload para horóscopo
$payload = @{
    birth_data = @{
        planets = $natalChart.planets
        houses = $natalChart.houses
    }
    timezone = $TIMEZONE
} | ConvertTo-Json -Depth 100

# 4. Obtener horóscopo del día
Write-Host "Obteniendo horóscopo del día..." -ForegroundColor Green
$horoscope = Invoke-RestMethod -Uri "$API_URL/horoscope/daily/" -Method Post `
    -ContentType "application/json" -Body $payload

# 5. Mostrar resultado
Write-Host "`nFecha:" -ForegroundColor Blue -NoNewline
Write-Host " $($horoscope.date)"

Write-Host "Ascendente:" -ForegroundColor Blue -NoNewline
Write-Host " $($horoscope.natal_ascendant)"

Write-Host "`nTop 3 Aspectos:" -ForegroundColor Blue
$horoscope.top_aspects[0..2] | ForEach-Object {
    Write-Host "  • $($_.transit_planet.ToUpper()) $($_.aspect) $($_.natal_planet.ToUpper()) (orbe: $([math]::Round($_.orb, 2))°)"
}

Write-Host "`nConsejo del día:" -ForegroundColor Blue
Write-Host $horoscope.interpretation.advice

# 6. Guardar horóscopo completo
$filename = "horoscope_$(Get-Date -Format 'yyyy-MM-dd').json"
$horoscope | ConvertTo-Json -Depth 100 | Out-File $filename
Write-Host "`n✓ Horóscopo guardado en $filename" -ForegroundColor Green
```

Ejecutar:
```powershell
.\horoscopo.ps1
```

---

## 7. Integración con Cron (Linux/Mac)

Enviar horóscopo diario por email cada mañana:

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar a las 7:00 AM)
0 7 * * * /path/to/horoscopo.sh | mail -s "Tu Horóscopo del Día" usuario@example.com
```

---

## 8. Webhooks - Notificar a otra aplicación

Obtener horóscopo y enviar a webhook:

```bash
#!/bin/bash

# Obtener horóscopo (usando script anterior)
HOROSCOPE=$(curl -s -X POST "http://localhost:8000/api/horoscope/daily/" \
  -H "Content-Type: application/json" \
  -d @horoscopo_payload.json)

# Extraer datos clave
CONSEJO=$(echo $HOROSCOPE | jq -r '.interpretation.advice')
FECHA=$(echo $HOROSCOPE | jq -r '.date')

# Enviar a webhook (ej: Slack, Discord, Telegram)
curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🌟 Horóscopo del '"$FECHA"'",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Consejo del día:*\n'"$CONSEJO"'"
        }
      }
    ]
  }'
```

---

## 9. Rate Limiting - Manejo de errores

```bash
#!/bin/bash

API_URL="http://localhost:8000/api"

# Función con reintentos
request_with_retry() {
    local url=$1
    local data=$2
    local max_retries=3
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
          -H "Content-Type: application/json" \
          -d "$data")
        
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [ "$http_code" -eq 200 ]; then
            echo "$body"
            return 0
        elif [ "$http_code" -eq 429 ]; then
            echo "Rate limit, esperando..." >&2
            sleep $((2 ** retry))
            retry=$((retry + 1))
        else
            echo "Error $http_code: $body" >&2
            return 1
        fi
    done
    
    echo "Max retries alcanzado" >&2
    return 1
}

# Uso
result=$(request_with_retry "$API_URL/horoscope/daily/" "$PAYLOAD")
```

---

## 10. Testing con diferentes usuarios

```bash
#!/bin/bash

# Array de usuarios
declare -a USERS=(
    "1992-12-07T23:58:00|America/Tegucigalpa|14.0723|-87.1921|Juan"
    "1995-03-15T10:30:00|America/Mexico_City|19.4326|-99.1332|María"
)

for user in "${USERS[@]}"; do
    IFS='|' read -r datetime timezone lat lon nombre <<< "$user"
    
    echo "Procesando $nombre..."
    
    # Calcular carta natal
    natal=$(curl -s -X POST "http://localhost:8000/api/compute/" \
      -H "Content-Type: application/json" \
      -d '{
        "datetime": "'"$datetime"'",
        "timezone": "'"$timezone"'",
        "latitude": '"$lat"',
        "longitude": '"$lon"',
        "house_system": "P",
        "topocentric_moon_only": false
      }')
    
    # Construir payload
    planets=$(echo $natal | jq -c '.planets')
    houses=$(echo $natal | jq -c '.houses')
    
    # Obtener horóscopo
    horoscope=$(curl -s -X POST "http://localhost:8000/api/horoscope/daily/" \
      -H "Content-Type: application/json" \
      -d '{
        "birth_data": {
          "planets": '"$planets"',
          "houses": '"$houses"'
        },
        "timezone": "'"$timezone"'"
      }')
    
    # Guardar
    echo $horoscope > "horoscope_$nombre.json"
    echo "✓ $nombre: $(echo $horoscope | jq -r '.interpretation.advice')"
done
```

---

## Notas

- **Producción**: Reemplazar `localhost:8000` con tu URL de producción
- **Seguridad**: Si agregas autenticación, incluir header: `-H "Authorization: Bearer TOKEN"`
- **Performance**: Cachear carta natal, solo re-calcular horóscopo diario
- **Error handling**: Siempre verificar códigos HTTP antes de procesar respuesta
