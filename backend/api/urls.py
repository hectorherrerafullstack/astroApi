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
from .views import health, compute_chart_view, daily_horoscope_view, transits_view

urlpatterns = [
    path("health/", health),
    path("compute/", compute_chart_view),
    path("horoscope/daily/", daily_horoscope_view),
    path("transits/", transits_view),
]