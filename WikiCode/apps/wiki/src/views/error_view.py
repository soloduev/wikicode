#   # -*- coding: utf-8 -*-
#
#   Copyright (C) 2016 Igor Soloduev <diahorver@gmail.com>
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



from django.shortcuts import render
from WikiCode.apps.wiki.src.views.auth import get_user_id, check_auth


def get_error_page(request, errors_arr):
    context = {
            "user_data": check_auth(request),
            "user_id": get_user_id(request),
            "error": errors_arr
        }
    return render(request, 'wiki/error.html', context)


def get_bug_report(request):
    context = {
        "user_data": check_auth(request),
        "user_id": get_user_id(request),
    }
    return render(request, 'wiki/bug_report.html', context)