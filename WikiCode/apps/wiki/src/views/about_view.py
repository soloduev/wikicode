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

from .auth import check_auth, get_user_id


def get_about(request, is_invite=False):
    with open("WikiCode/apps/wiki/docs/1.1.Description.md", "r", encoding='utf-8') as f:
        about_wikicode = f.read()

    context = {
        "user_data" : check_auth(request),
        "user_id": get_user_id(request),
        "about_wikicode":about_wikicode,
    }

    if not is_invite:
        return render(request, 'wiki/about.html', context)
    else:
        return render(request, 'wiki/about_invite.html', context)