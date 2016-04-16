# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse
from django.shortcuts import render

from WikiCode.apps.wiki.wiki_settings import wiki_settings
from .auth import check_auth, get_user_id
from WikiCode.apps.wiki.models import User, Publication, Statistics
from WikiCode.apps.wiki.my_libs.trees_management.manager import WikiTree


def get_tree_manager(request):

    user_data = check_auth(request)
    try:
        user = User.objects.get(email=user_data)
        wt = WikiTree(user.id_user)
        wt.load_tree(user.tree)

        context = {
            "user_data": user_data,
            "user_id": get_user_id(request),
            "preview_tree": wt.generate_html_preview(),
            "dynamic_tree": wt.generate_html_dynamic(),
        }

        return render(request, 'wiki/tree_manager.html', context)
    except User.DoesNotExist:
        context = {
            "user_data": user_data,
            "user_id": get_user_id(request),
        }
        return render(request, 'wiki/tree_manager.html', context)


def get_add_folder_in_tree(request):
    """Ajax представление. Добавление папки в дерево пользователя"""

    if request.method == "GET":
        answer = request.GET.get('answer')
        user_data = check_auth(request)
        split_answer = answer.split("^^^")
        folder_name = split_answer[0]
        path = split_answer[1].split(":")[0]

        try:
            user = User.objects.get(email=user_data)
            wt = WikiTree(user.id_user)
            wt.load_tree(user.tree)
            wt.add_folder(path,folder_name)
            user.tree = wt.get_tree()
            user.save()

            return HttpResponse('ok', content_type='text/html')

        except User.DoesNotExist:
            context = {
                "user_data": user_data,
                "user_id": get_user_id(request),
            }
            return render(request, 'wiki/tree_manager.html', context)

    else:
        return HttpResponse('no', content_type='text/html')


def get_del_elem_in_tree(request):
    """Ajax представление. Удаление элемента в дереве пользователя"""

    return HttpResponse('ok', content_type='text/html')


def get_delete_publ_in_tree(request):
    """Ajax представление. Удаление конспекта."""

    if request.method == "GET":
        path_publ = request.GET.get('answer')
        user_data = check_auth(request)
        arr = path_publ.split(":")
        id_publ = arr[1]

        try:
            # Получаем удаляемую публикацию
            publication = Publication.objects.get(id_publication=id_publ)
            # Получаем автора этой публикации
            user = User.objects.get(email=user_data)
            # Получаем статистику сайта
            stat = Statistics.objects.get(id_statistics=1)

            # Начинаем производить достаточно громоздкое удаление

            # Получаем дерево пользователя

            # Устанавливаем id пользователя
            wt = WikiTree(user.id_user)
            # Загружаем его дерево
            wt.load_tree(user.tree)
            # Удаляем публикацию по указанному пути
            wt.delete_publication(arr[0])
            user.tree = wt.get_tree()

            # Уменьшаем количество публикаций у пользователя
            user.publications -= 1
            # Уменьшаем количество публикаций в глобальной статистике
            stat.publications_delete += 1

            # Удаляем html файл этой публикации
            os.remove(wiki_settings.DELETE_PUBLICATION_PATH + str(id_publ) +".html")

            publication.delete()
            user.save()
            stat.save()

            return HttpResponse('ok', content_type='text/html')

        except Publication.DoesNotExist:
            return HttpResponse('no', content_type='text/html')
        except User.DoesNotExist:
            return HttpResponse('no', content_type='text/html')
        except Statistics.DoesNotExist:
            return HttpResponse('no', content_type='text/html')

    else:
        return HttpResponse('no', content_type='text/html')