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


# Все чисто джанговские методы и классы находятся здесь, скрытые от посторонних глаз

# DJANGO METHODS
from django.shortcuts import redirect

# WRAPPERS DJANGO METHODS
from WikiCode.apps.wiki.src.views.auth import get_user_id
from WikiCode.apps.wiki.src.views.error_view import get_error_page

# MODELS
from WikiCode.apps.wiki.models import User
from WikiCode.apps.wiki.models import Group
from WikiCode.apps.wiki.models import InviteKeys

# MODULES
from WikiCode.apps.wiki.src.modules.wiki_tree.wiki_tree import WikiFileTree
from WikiCode.apps.wiki.src.modules.wiki_permissions.wiki_permissions import WikiPermissions

# PYTHON CORE LIBS
import random