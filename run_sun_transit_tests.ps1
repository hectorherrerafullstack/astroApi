# Script para ejecutar tests de la nueva ruta /api/sun-transit/ en Windows
# Uso: .\run_sun_transit_tests.ps1

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Tests para GET /api/sun-transit/                             ║" -ForegroundColor Cyan
Write-Host "║  Ruta de Tránsito Diario del Sol                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Navegar al directorio backend
$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath

Write-Host "Directorio actual: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Verificar si el entorno virtual está activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Entorno virtual no activado. Por favor activa el entorno virtual primero:" -ForegroundColor Yellow
    Write-Host "   Windows CMD: entorno\Scripts\activate.bat" -ForegroundColor Gray
    Write-Host "   PowerShell: entorno\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "✅ Entorno virtual activo: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

Write-Host "Ejecutando tests de la API del tránsito solar..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Tests básicos de funcionalidad
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "GRUPO 1: Tests de Funcionalidad Básica" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
python manage.py test api.test_sun_transit.SunTransitDailyTestCase -v 2

# Verificar resultado
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error en tests de funcionalidad" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "GRUPO 2: Tests de Validación de Datos" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
python manage.py test api.test_sun_transit.SunTransitDataValidationTestCase -v 2

# Verificar resultado
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error en tests de validación" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "GRUPO 3: Tests de Performance/Caché" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
python manage.py test api.test_sun_transit.SunTransitPerformanceTestCase -v 2

# Verificar resultado
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error en tests de performance" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ TODOS LOS TESTS PASARON CORRECTAMENTE                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "Resumen de tests ejecutados:" -ForegroundColor Cyan
Write-Host "  • 10 Tests de Funcionalidad Básica" -ForegroundColor Gray
Write-Host "  • 3 Tests de Validación de Datos" -ForegroundColor Gray
Write-Host "  • 1 Test de Performance/Caché" -ForegroundColor Gray
Write-Host ""

Write-Host "La ruta /api/sun-transit/ está funcionando correctamente ✨" -ForegroundColor Green
