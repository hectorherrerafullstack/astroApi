/**
 * Cliente JavaScript para API de Horóscopo Diario
 * Ejemplo de integración para aplicaciones frontend
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Cliente para la API de astrología
 */
class AstroAPIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Calcula la carta natal del usuario (hacer una sola vez)
   */
  async calculateNatalChart(birthData) {
    const response = await fetch(`${this.baseURL}/compute/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(birthData),
    });

    if (!response.ok) {
      throw new Error(`Error calculando carta natal: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Obtiene el horóscopo diario personalizado
   */
  async getDailyHoroscope(natalChart, targetDate = null, timezone = 'UTC') {
    const payload = {
      birth_data: {
        planets: natalChart.planets,
        houses: natalChart.houses,
      },
      timezone,
    };

    if (targetDate) {
      payload.target_date = targetDate; // formato: "YYYY-MM-DD"
    }

    const response = await fetch(`${this.baseURL}/horoscope/daily/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Error obteniendo horóscopo: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Obtiene tránsitos planetarios para una fecha
   */
  async getTransits(date = null, timezone = 'UTC') {
    const params = new URLSearchParams({ timezone });
    if (date) {
      params.append('date', date);
    }

    const response = await fetch(`${this.baseURL}/transits/?${params}`);

    if (!response.ok) {
      throw new Error(`Error obteniendo tránsitos: ${response.statusText}`);
    }

    return await response.json();
  }
}

/**
 * Formateador de horóscopos para UI
 */
class HoroscopeFormatter {
  /**
   * Formatea aspectos para mostrar en UI
   */
  static formatAspect(aspect) {
    const emoji = {
      'Conjunción': '☌',
      'Sextil': '⚹',
      'Cuadratura': '□',
      'Trígono': '△',
      'Oposición': '☍',
    };

    const quality = {
      'Conjunción': 'neutral',
      'Sextil': 'positive',
      'Cuadratura': 'challenging',
      'Trígono': 'positive',
      'Oposición': 'challenging',
    };

    return {
      icon: emoji[aspect.aspect] || '○',
      quality: quality[aspect.aspect] || 'neutral',
      text: `${this.capitalize(aspect.transit_planet)} ${emoji[aspect.aspect]} ${this.capitalize(aspect.natal_planet)}`,
      description: aspect.aspect,
      orb: aspect.orb.toFixed(2),
      applying: aspect.applying,
    };
  }

  /**
   * Formatea casas activadas
   */
  static formatHouse(houseData) {
    const houseNames = {
      1: 'Identidad',
      2: 'Recursos',
      3: 'Comunicación',
      4: 'Hogar',
      5: 'Creatividad',
      6: 'Salud',
      7: 'Pareja',
      8: 'Transformación',
      9: 'Expansión',
      10: 'Carrera',
      11: 'Amistades',
      12: 'Espiritualidad',
    };

    const planetsText = houseData.planets
      .map((p) => this.capitalize(p.planet))
      .join(', ');

    return {
      number: houseData.house,
      name: houseNames[houseData.house],
      planets: planetsText,
      weight: houseData.weight,
    };
  }

  /**
   * Capitaliza primera letra
   */
  static capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  /**
   * Genera HTML para mostrar horóscopo
   */
  static toHTML(horoscope) {
    let html = `
      <div class="daily-horoscope">
        <h2>Tu Horóscopo del ${horoscope.date}</h2>
        <p class="ascendant">Ascendente: ${horoscope.natal_ascendant}</p>
        
        <section class="aspects">
          <h3>⭐ Aspectos Clave del Día</h3>
          <ul>
    `;

    horoscope.top_aspects.slice(0, 3).forEach((aspect) => {
      const formatted = this.formatAspect(aspect);
      const applyingText = aspect.applying ? '📈 Aplicativo' : '📉 Separativo';
      html += `
        <li class="aspect ${formatted.quality}">
          <span class="aspect-icon">${formatted.icon}</span>
          <strong>${formatted.text}</strong> - ${formatted.description}
          <br>
          <small>Orbe: ${formatted.orb}° | ${applyingText}</small>
        </li>
      `;
    });

    html += `
          </ul>
        </section>
        
        <section class="houses">
          <h3>🏠 Áreas de Vida Activadas</h3>
          <ul>
    `;

    horoscope.houses_activated.forEach((house) => {
      const formatted = this.formatHouse(house);
      html += `
        <li class="house">
          <strong>Casa ${formatted.number} (${formatted.name})</strong>
          <br>
          <small>Activada por: ${formatted.planets}</small>
        </li>
      `;
    });

    html += `
          </ul>
        </section>
        
        <section class="interpretation">
          <h3>📖 Interpretación</h3>
          <div class="summary">${this.formatText(horoscope.interpretation.summary)}</div>
        </section>
        
        <section class="advice">
          <h3>💡 Consejo del Día</h3>
          <p class="advice-text">${horoscope.interpretation.advice}</p>
        </section>
      </div>
    `;

    return html;
  }

  /**
   * Convierte markdown simple a HTML
   */
  static formatText(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }
}

/**
 * Ejemplo de uso completo
 */
async function ejemploCompleto() {
  const client = new AstroAPIClient();

  try {
    // 1. Calcular carta natal (hacer una vez y guardar en localStorage/DB)
    console.log('Calculando carta natal...');
    const natalChart = await client.calculateNatalChart({
      datetime: '1992-12-07T23:58:00',
      timezone: 'America/Tegucigalpa',
      latitude: 14.0723,
      longitude: -87.1921,
      house_system: 'P',
      topocentric_moon_only: false,
    });

    console.log('Carta natal calculada:', natalChart);

    // Guardar en localStorage para uso futuro
    localStorage.setItem('natalChart', JSON.stringify(natalChart));

    // 2. Obtener horóscopo del día
    console.log('Obteniendo horóscopo del día...');
    const horoscope = await client.getDailyHoroscope(
      natalChart,
      null, // null = hoy
      'America/Tegucigalpa'
    );

    console.log('Horóscopo del día:', horoscope);

    // 3. Generar HTML y mostrar
    const html = HoroscopeFormatter.toHTML(horoscope);
    document.getElementById('horoscope-container').innerHTML = html;

    // 4. También podemos obtener solo tránsitos
    const transits = await client.getTransits(null, 'America/Tegucigalpa');
    console.log('Tránsitos del día:', transits);

  } catch (error) {
    console.error('Error:', error);
    document.getElementById('horoscope-container').innerHTML = `
      <div class="error">
        <h3>Error al obtener horóscopo</h3>
        <p>${error.message}</p>
      </div>
    `;
  }
}

/**
 * Uso optimizado: solo obtener horóscopo (asumiendo que ya tienes carta natal)
 */
async function obtenerHoroscopoRapido() {
  const client = new AstroAPIClient();

  // Recuperar carta natal de localStorage
  const natalChartJSON = localStorage.getItem('natalChart');
  if (!natalChartJSON) {
    console.error('No hay carta natal guardada. Ejecuta ejemploCompleto() primero.');
    return;
  }

  const natalChart = JSON.parse(natalChartJSON);

  // Obtener horóscopo del día
  const horoscope = await client.getDailyHoroscope(
    natalChart,
    null,
    'America/Tegucigalpa'
  );

  // Mostrar
  const html = HoroscopeFormatter.toHTML(horoscope);
  document.getElementById('horoscope-container').innerHTML = html;

  return horoscope;
}

/**
 * Obtener horóscopo para una fecha específica
 */
async function obtenerHoroscopoPorFecha(fecha) {
  const client = new AstroAPIClient();
  const natalChart = JSON.parse(localStorage.getItem('natalChart'));

  const horoscope = await client.getDailyHoroscope(
    natalChart,
    fecha, // formato "YYYY-MM-DD"
    'America/Tegucigalpa'
  );

  return horoscope;
}

/**
 * Sistema de caché para optimizar requests
 */
class HoroscopeCache {
  constructor(client) {
    this.client = client;
    this.cache = new Map();
  }

  /**
   * Obtiene horóscopo con caché (evita requests duplicados)
   */
  async getDailyHoroscope(natalChart, date = null, timezone = 'UTC') {
    const today = date || new Date().toISOString().split('T')[0];
    const cacheKey = `${today}-${timezone}`;

    // Verificar caché
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      const age = Date.now() - cached.timestamp;

      // Caché válido por 6 horas
      if (age < 6 * 60 * 60 * 1000) {
        console.log('Usando horóscopo desde caché');
        return cached.data;
      }
    }

    // Obtener nuevo horóscopo
    const horoscope = await this.client.getDailyHoroscope(natalChart, date, timezone);

    // Guardar en caché
    this.cache.set(cacheKey, {
      data: horoscope,
      timestamp: Date.now(),
    });

    return horoscope;
  }

  /**
   * Limpia caché antiguo
   */
  clearOldCache() {
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24 horas

    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > maxAge) {
        this.cache.delete(key);
      }
    }
  }
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AstroAPIClient,
    HoroscopeFormatter,
    HoroscopeCache,
  };
}
