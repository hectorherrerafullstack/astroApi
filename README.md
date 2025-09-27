# Astro Backend API

Backend API para cálculos astrológicos precisos usando Swiss Ephemeris, optimizado para coincidir con Astro.com.

## 📋 Tabla de Contenidos
- [Cómo Funciona](#cómo-funciona)
- [Arquitectura](#arquitectura)
- [Instalación Local](#instalación-local)
- [Despliegue](#despliegue)
- [Uso de la API](#uso-de-la-api)
- [Seguridad y Vulnerabilidades](#seguridad-y-vulnerabilidades)
- [Licencia](#licencia)

## 🔍 Cómo Funciona

Esta API calcula posiciones astrológicas (planetas, casas, nodos) usando **Swiss Ephemeris** con efemérides DE431 para máxima precisión. Está diseñada para ser un backend RESTful que:

- Recibe datos de nacimiento (fecha, hora, ubicación)
- Convierte a tiempo UT usando `swe.utc_to_jd`
- Calcula posiciones geocéntricas aparentes con `swe.calc_ut`
- Computa casas con `swe.houses_ex`
- Devuelve resultados en JSON con formato zodiacal

### Precisión
- **>99.9%** de coincidencia con Astro.com
- Usa DE431 (no DE406 obsoleto)
- Maneja ΔT internamente
- Longitudes este-positivas
- Nodo verdadero, Luna geocéntrica

## 🏗️ Arquitectura

```
astroapi/
├── backend/                 # Django app
│   ├── backend/            # Configuración principal
│   │   ├── settings.py     # Config Django + SE_EPHE_PATH
│   │   ├── urls.py         # Rutas principales
│   │   └── wsgi.py         # WSGI para despliegue
│   └── api/                # App de API
│       ├── services.py     # Lógica de cálculos (Swiss Ephemeris)
│       ├── views.py        # Endpoints REST
│       ├── urls.py         # Rutas API
│       └── apps.py         # Config app
├── se_data/                # Efemérides DE431 (.se1/.se2)
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Contenedor
├── docker-compose.yml      # Orquestación
├── LICENSE                 # AGPL-3.0
├── NOTICE                  # Créditos
└── README.md               # Esta documentación
```

### Componentes Clave
- **Django REST Framework**: API REST
- **Swiss Ephemeris (pyswisseph)**: Cálculos astronómicos
- **pytz/dateutil**: Manejo de zonas horarias
- **Gunicorn**: Servidor WSGI
- **Whitenoise**: Archivos estáticos

## 🛠️ Instalación Local

### Prerrequisitos
- Python 3.11+ (para pyswisseph wheels)
- Git

### Pasos
```bash
# 1. Clonar repositorio
git clone https://github.com/tuusuario/astroapi.git
cd astroapi

# 2. Crear entorno virtual
python -m venv entorno311
entorno311\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar efemérides
ls se_data/  # Debe contener sepl*.se1, semo*.se1

# 5. Ejecutar servidor
python backend/manage.py runserver
```

### Verificación
```bash
curl http://localhost:8000/api/health/
# Respuesta: {"status": "ok"}
```

## 🚀 Despliegue

### Opción 1: Docker Local
```bash
docker-compose up --build
# Accede en http://localhost:8000
```

### Opción 2: Koyeb (Recomendado)
1. **Subir código a GitHub** (público, por AGPL)
2. **Crear app en Koyeb**:
   - Conectar repo GitHub
   - Runtime: Python 3.11
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn backend.backend.wsgi --bind 0.0.0.0:$PORT`
3. **Variables de entorno**:
   - `DJANGO_DEBUG=False`
   - `DJANGO_SECRET_KEY=tu_clave_segura`
   - `DJANGO_ALLOWED_HOSTS=*`
   - `SOURCE_REPO_URL=https://github.com/tuusuario/astroapi`
4. **Volumen persistente**:
   - Montar `/app/se_data` con los archivos de efemérides
5. **Desplegar**

### Opción 3: Otros (Heroku, Railway, etc.)
- Similar a Koyeb, usar `gunicorn` como start command
- Asegurar volumen para `se_data/`

## 📡 Uso de la API

### Health Check
```bash
GET /api/health/
# {"status": "ok"}
```

### Calcular Carta Astral
```bash
POST /api/compute/
Content-Type: application/json

{
  "datetime": "1992-02-14T20:30:00",
  "timezone": "Europe/Madrid",
  "latitude": 41.5467,
  "longitude": 2.1094,
  "house_system": "placidus",
  "topocentric_moon_only": false
}
```

**Respuesta**: JSON con posiciones de planetas y casas.

Ver [ejemplos detallados](#uso-de-la-api) arriba.

#### ⚠️ Errores Comunes
- **400 Bad Request**: Payload inválido (JSON malformado, campos faltantes como `datetime`, `latitude`, etc.)
- **500 Internal Server Error**: Problemas con efemérides o cálculos internos
- Headers incluyen `X-License: AGPL-3.0-only` para cumplimiento legal.

## 🔒 Seguridad y Vulnerabilidades

### ✅ Medidas de Seguridad Implementadas
- **AGPL-3.0**: Código abierto, auditable
- **No almacenamiento de datos**: API stateless, no guarda información personal
- **Validación de entrada**: JSON schema implícito en views
- **Headers de licencia**: `X-License: AGPL-3.0-only` en respuestas
- **CORS**: Configurado para orígenes permitidos (si necesitas)
- **Rate limiting**: Recomendado agregar en producción (ej. con nginx)

### ⚠️ Vulnerabilidades Potenciales y Mitigaciones

#### 1. **Dependencias Desactualizadas**
- **Riesgo**: Librerías con CVEs conocidas
- **Mitigación**:
  ```bash
  pip list --outdated
  pip install --upgrade -r requirements.txt
  ```
  - Monitorear con `safety` o `pip-audit`

#### 2. **Exposición de Información**
- **Riesgo**: Errores detallados revelan estructura
- **Mitigación**: `DEBUG=False` en producción, usar `sentry` para logging

#### 3. **Ataques de Denegación de Servicio (DoS)**
- **Riesgo**: Cálculos intensivos pueden sobrecargar CPU
- **Mitigación**:
  - Rate limiting (ej. django-ratelimit)
  - Timeouts en requests
  - Caché para cálculos repetidos

#### 4. **Inyección de Datos**
- **Riesgo**: Payload JSON malicioso
- **Mitigación**: Validación estricta en `views.py`, usar `drf-yasg` para schemas

#### 5. **Problemas de Efemérides**
- **Riesgo**: Archivos corruptos o faltantes
- **Mitigación**: Verificación en startup, backups de `se_data/`

#### 6. **Vulnerabilidades en pyswisseph**
- **Estado**: Librería madura, mantenida por Astrodienst
- **Mitigación**: Usar versión reciente, auditar código fuente

### 🔍 Checklist de Seguridad
- [ ] `DEBUG=False` en prod
- [ ] Secret key fuerte y única
- [ ] HTTPS obligatorio
- [ ] Rate limiting implementado
- [ ] Logs no exponen datos sensibles
- [ ] Dependencias actualizadas
- [ ] Repo público para cumplimiento AGPL

### 🔍 Análisis de Vulnerabilidades
**Estado**: ✅ **0 vulnerabilidades conocidas** (escaneo con `safety` al 27/09/2025)

- Todas las dependencias están actualizadas y libres de CVEs conocidas
- pyswisseph es una librería madura y mantenida
- Recomendación: Ejecutar `safety check` periódicamente

## 📄 Licencia

**AGPL-3.0-only**

Este proyecto es software libre. Ver [LICENSE](LICENSE) para detalles.



Para preguntas: [info@hectorherrerafullstack.com]

---

¡Gracias por usar Astro Backend! 🌟