#   # -*- coding: utf-8 -*-
#
#   Copyright (C) 2016-2017 Igor Soloduev <diahorver@gmail.com>
#
#   This file is part of WikiCode.
#
#   WikiCode is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   WikiCode is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with WikiCode.  If not, see <http://www.gnu.org/licenses/>.


# ------------------------------------------------------
# -------------------- WikiCode API --------------------
# ------------------------------------------------------

from WikiCode.apps.wiki.src.engine.src.notifications import notify
from WikiCode.apps.wiki.src.engine.src.admin import admin
from WikiCode.apps.wiki.src.engine.src import djangoapi as __djangoapi


def goto(html_page: str):
    return __djangoapi.redirect(html_page)


def goerror(request, errors: list):
    return __djangoapi.get_error_page(request, errors)


