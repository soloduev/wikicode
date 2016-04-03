# -*- coding: utf-8 -*-
from django.shortcuts import render

from .auth import check_auth


def get_tree_manager(request):

    context = {
        "user_data": check_auth(request),
    }

    return render(request, 'wiki/tree_manager.html', context)
