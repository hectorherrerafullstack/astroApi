# This file is part of astroapi.
#
# astroapi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# astroapi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with astroapi.  If not, see <https://www.gnu.org/licenses/>.

from django.urls import path
from .views import health, compute_chart_view, planet_transits_view, daily_horoscope_view, transits_view, monthly_transits_view, cache_stats_view, sun_transit_daily_view, weekly_climate_view, daily_planetary_positions_view, eclipses_view

urlpatterns = [
    path("health/", health, name="health"),
    path("compute/", compute_chart_view, name="compute_chart"),
    path("planet-transits/", planet_transits_view, name="planet_transits"),
    path("horoscope/daily/", daily_horoscope_view, name="daily_horoscope"),
    path("transits/", transits_view, name="transits"),
    path("moon/", transits_view, name="moon_daily"),
    path("sun-transit/", sun_transit_daily_view, name="sun_transit_daily"),
    path("weekly-climate/", weekly_climate_view, name="weekly_climate"),
    path("daily-positions/", daily_planetary_positions_view, name="daily_planetary_positions"),
    path("monthly-transits/<int:month>/<int:year>/", monthly_transits_view, name="monthly_transits"),
    path("eclipses/", eclipses_view, name="eclipses"),
    path("cache/stats/", cache_stats_view, name="cache_stats"),
]