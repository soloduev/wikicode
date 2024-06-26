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


import datetime
import json

from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from WikiCode.apps.wiki.models import Publication, Statistics, Viewing, DynamicParagraph, Comment, Folder, Starring
from WikiCode.apps.wiki.models import User, CommentRating, Tag
import configuration as wiki_settings
from WikiCode.apps.wiki.src.modules.wiki_comments.wiki_comments import WikiComments
from WikiCode.apps.wiki.src.modules.wiki_permissions.wiki_permissions import WikiPermissions
from WikiCode.apps.wiki.src.modules.wiki_tree.wiki_tree import WikiFileTree
from WikiCode.apps.wiki.src.modules.wiki_versions.wiki_versions import WikiVersions
from WikiCode.apps.wiki.src.engine import wcode
from WikiCode.apps.wiki.src.wiki_markdown import WikiMarkdown
from .auth import check_auth, get_user_id


def get_create(request):
    user_data = check_auth(request)
    try:
        # Получения id папки, в которой хотим создать конспект
        input_folder_id = ""
        path_folder = ""
        full_path = str(request.POST.get('folder_publ'))

        user = User.objects.get(email=user_data)

        wft = WikiFileTree()
        wft.load_tree(user.file_tree)

        if full_path != "None" and full_path != "NONE":
            input_folder_id = full_path
            path_folder = wft.get_path_folder(int(full_path.split(":")[1]))

        # Проверяем, не пустует ли его дерево:
        if wft.get_num_root_folders() == 0:
            empty_tree = True
        else:
            empty_tree = False

        context = {
            "user_data": user_data,
            "user_id": get_user_id(request),
            "dynamic_tree": wft.to_html_dynamic_folders(),
            "path": input_folder_id,
            "show_path": path_folder,
            "empty_tree": empty_tree,
        }

        return render(request, 'wiki/create.html', context)
    except User.DoesNotExist:
        context = {
            "user_data": user_data,
            "user_id": get_user_id(request),
        }
        return render(request, 'wiki/create.html', context)


def get_page(request, id):
    """ Возвращает страницу конспекта."""

    try:
        cur_user_id = get_user_id(request)
        publication = Publication.objects.get(id_publication=id)

        try:
            user = User.objects.get(id_user=publication.id_author)
            wft = WikiFileTree()
            wft.load_tree(user.file_tree)
        except User.DoesNotExist:
            return wcode.goerror(request, ["Не удалось загрузить юзера. Его уже не существует!"])

        # Проверяем доступ пользователя к конспекту
        wp = WikiPermissions()
        wp.load_permissions(publication.permissions)
        black_list = wp.get_black_list()
        white_list = wp.get_white_list()

        # Проверяем, не находится ли пользователь в черном списке
        for black_user in black_list:
            if str(cur_user_id) == str(black_user["id"]):
                return wcode.goerror(request, ["У Вас нет прав доступа к этому конспекту."])

        # Проверяем, не находится ли пользователь в списке редакторов
        is_editor = False
        for white_user in white_list:
            if str(cur_user_id) == str(white_user["id"]):
                is_editor = True
                break

        # Если конспект приватный и пользователь не является редактором конспекта, то блокируем ему доступ
        if not publication.is_public and not is_editor and publication.id_author != cur_user_id:
            return wcode.goerror(request, ["У Вас нет прав доступа к этому конспекту."])

        # Смотрим, может ли пользователь редактировать конспект.
        # Если конспект не защищен от редактирования или пользователь является редактором/автором конспекта, то конспект
        # редактируемый
        if not publication.is_protected_edit or is_editor or publication.id_author == cur_user_id:
            is_editable = True
        else:
            is_editable = False

        # Разбиваем весь текст на абзацы
        md_text = publication.text
        wm = WikiMarkdown()
        arr = wm.split(md_text)
        numbers = []
        paragraphs = []
        for i in range(0, len(arr)):
            numbers.append(str(i + 1))
            paragraphs.append({
                "index": str(i + 1),
                "text": arr[i]
            })

        # Загружаем превью дерево автора
        try:
            author_user = User.objects.get(id_user=publication.id_author)

            wft = WikiFileTree()
            wft.load_tree(author_user.file_tree)
            if author_user.id_user == cur_user_id:
                html_preview_tree = wft.to_html_preview()
            else:
                html_preview_tree = wft.to_html_preview(only_public=True)
        except User.DoesNotExist:
            print("Автора не существует")

        # Загружаем все динамические комментарии в этой публикации
        if wiki_settings.MODULE_DYNAMIC_PARAGRAPHS:
            arr_dynamic_paragraphs = DynamicParagraph.objects.filter(publication=publication)
            dynamic_comments = []
            # Далее, к составляем расширенный массив, с именем автора
            wc = WikiComments()
            for dynamic_paragraph in arr_dynamic_paragraphs:
                wc.load_comments(dynamic_paragraph.comments)
                dynamic_comments.append({
                    "publication": dynamic_paragraph.publication,
                    "paragraph": dynamic_paragraph.paragraph,
                    "dynamic_comments": wc.to_html(is_dynamic=True)
                })

        else:
            dynamic_comments = None

        if wiki_settings.MODULE_VERSIONS:
            wiki_version = WikiVersions()
            wiki_version.load_versions(publication.versions)
            versions_js = wiki_version.generate_js()
        else:
            versions_js = None

        # Конвертируем общие комментарии
        wiki_comments = WikiComments()
        wiki_comments.load_comments(publication.main_comments)

        # Добавим конспекту просмотр, если этот пользователь еще не смотрел этот конспект
        try:
            viewing = Viewing.objects.get(id_user=cur_user_id, id_publ=id)
            # Просмотр стоит, ничего не добавляем
        except Viewing.DoesNotExist:
            # Просмотр не стоит. Ставим

            # Получаем текущую дату
            date = str(datetime.datetime.now())
            date = date[:len(date) - 7]

            new_viewing = Viewing(id_user=cur_user_id,
                                  nickname=user.nickname,
                                  id_publ=id,
                                  date=date)
            new_viewing.save()
            publication.read += 1
            publication.save()

        # Генерируем оглавление для конспекта
        contents = wm.generate_contents(paragraphs, publication.id_publication)

        # Получаем файловое дерево пользователя, для сохранения конспекта
        try:
            if cur_user_id != -1:
                cur_user = User.objects.get(id_user=cur_user_id)
                wft = WikiFileTree()
                wft.load_tree(cur_user.file_tree)
                dynamic_tree = wft.to_html_dynamic_folders()
            else:
                dynamic_tree = None
        except User.DoesNotExist:
            return wcode.goerror(request, ["Пользователя не сущесвует"])

        # Узнаем, ставил ли звезду, этот пользователь, этому конспекту
        try:
            starring = Starring.objects.get(id_user=cur_user_id, id_publ=publication.id_publication)
            is_star = True
        except Starring.DoesNotExist:
            is_star = False

        # Получаем теги конспекта
        try:
            tags = Tag.objects.filter(to_id=id, type="publ")
        except Tag.DoesNotExist:
            tags = None

        context = {
            "publication": publication,
            "paragraphs": paragraphs,
            "numbers": numbers,
            "user_data": check_auth(request),
            "user_id": cur_user_id,
            "preview_tree": html_preview_tree,
            "dynamic_tree": dynamic_tree,
            "module_dynamic_paragraphs": wiki_settings.MODULE_DYNAMIC_PARAGRAPHS,
            "dynamic_comments": dynamic_comments,
            "module_main_comments": wiki_settings.MODULE_MAIN_COMMENTS,
            "main_comments": wiki_comments.to_html(),
            "main_comments_count": wiki_comments.get_count(),
            "module_versions": wiki_settings.MODULE_VERSIONS,
            "versions_js": versions_js,
            "contents": contents,
            "is_editable": is_editable,
            "is_star": is_star,
            "tags": tags,
            "notify": wcode.notify.instant.get(request),
        }

        return render(request, 'wiki/page/page.html', context)
    except Publication.DoesNotExist:
        return wcode.goerror(request, ["This is publication not found!", "Page not found: page/" + str(id) + "/"])


def get_create_page(request):
    # Получаем данные формы
    form = request.POST
    # Получаем пользователя
    user_data = check_auth(request)
    try:
        user = User.objects.get(email=user_data)
    except User.DoesNotExist:
        return wcode.goerror(request, ["Пользователя, создающего конспект не существует!"])
    # Проверяем, чего хотим сделать
    if request.POST.get('secret') == "off":
        with open("WikiCode/apps/wiki/generate_pages/gen_page.gen", "r", encoding='utf-8') as f:
            gen_page = f.read()
        first_part = "<!DOCTYPE html><html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"><title>" + \
                     form["title"] + '</title></head><xmp theme="' + form[
                         "theme"].lower() + '" style="display:none;">'
        second_part = form["text"]
        ready_page = first_part + second_part + gen_page
        stat = Statistics.objects.get(id_statistics=1)
        num = stat.publications_create
        stat.publications_create += 1

        newid = num + 1

        # Перед тем, как создать публикацию, проверяем, не существует ли она уже
        try:
            publ = Publication.objects.get(id_publication=newid)
            return wcode.goerror(request, ["Конспект с таким id уже существует!"])
        except Publication.DoesNotExist:
            # Создаем первые комментарии
            wiki_comments = WikiComments()
            wiki_comments.create_comments(newid)

            # Создаем первую версию конспекта
            wiki_versions = WikiVersions()
            wm = WikiMarkdown()  # Получаем все абзацы
            paragraphs = wm.split(form["text"])
            wiki_versions.create_versions(id_user=user.id_user,
                                          seq=list(paragraphs))
            archive = wiki_versions.get_archive()

            # Создаем уровни доступа к конспекту
            wp = WikiPermissions()
            wp.create_permissions(id=newid, id_creator=user.id_user)

            # Получаем все теги конспекта и сохраняем их
            tags = form["array-tags"].split(",")
            new_tags = []
            if tags[0] != '':
                # Проходим по всем тегам, и создаем их
                for tag in tags:
                    # Создаем новый тег, если его к этому конспекту не существует
                    try:
                        some_tag = Tag.objects.get(name=tag, type="publ", to_id=newid)
                    except Tag.DoesNotExist:
                        new_tag = Tag(name=tag, type="publ", to_id=newid)
                        new_tags.append(new_tag)

            new_publication = Publication(
                id_publication=newid,
                id_author=user.id_user,
                nickname_author=user.nickname,
                title=form["title"],
                description=form["description"],
                text=form["text"],
                theme=form["theme"],
                html_page=ready_page,
                tree_path=form["folder"],
                read=0,
                stars=0,
                saves=0,
                main_comments=wiki_comments.get_xml_str(),
                versions=archive,
                permissions=wp.get_xml_str(),
                is_public=request.POST.get("access-opt", False),
                is_dynamic_paragraphs=request.POST.get("dynamic-opt", False),
                is_general_comments=request.POST.get("main-comments-opt", False),
                is_contents=request.POST.get("contents-opt", False),
                is_protected_edit=request.POST.get("private-edit-opt", False),
                is_files=request.POST.get("files-opt", False),
                is_links=request.POST.get("links-opt", False),
                is_versions=request.POST.get("versions-opt", False),
                is_show_author=request.POST.get("show-author-opt", False),
                is_loading=request.POST.get("loading-opt", False),
                is_saving=request.POST.get("saving-opt", False),
                is_starring=request.POST.get("rating-opt", False),
                is_file_tree=request.POST.get("file-tree-opt", False)
            )

        # Загружаем дерево пользователя
        wft = WikiFileTree()
        wft.load_tree(user.file_tree)

        # Добавляем этот конспект в папку
        wft.create_publication(id=newid,
                               name=form["title"],
                               access="public" if request.POST.get("access-opt", False) else "private",
                               type="personal",
                               id_folder=form['folder'].split(':')[1])  # new version

        user.file_tree = wft.get_xml_str()  # new version

        # Увеличиваем количество публикаций в статистике у пользователя
        user.publications += 1

        # Сохраняем все новые данные

        # Новые теги
        for tag in new_tags:
            tag.save()
        # Статистика
        stat.save()
        # Конспект
        new_publication.save()
        # Пользователь

        user.save()
        return HttpResponseRedirect("/")
    else:
        first_part = '<!DOCTYPE html><html><title>' + form["title"] + '</title><xmp theme="' + form[
            "theme"].lower() + '" style="display:none;">'
        second_part = form["text"]
        third_part = '</xmp><script src="http://strapdownjs.com/v/0.2/strapdown.js"></script></html>'
        total = first_part + second_part + third_part
        return HttpResponse(total)


def get_presentation(request, id):
    # Получаем данные формы
    try:
        publication = Publication.objects.get(id_publication=id)
        # Составляем страницу презентации конспекта
        first_part = '<!DOCTYPE html><html><title>' + publication.title + '</title><xmp theme="' + publication.theme.lower() + '" style="display:none;">'
        second_part = publication.text
        third_part = '</xmp><script src="http://strapdownjs.com/v/0.2/strapdown.js"></script></html>'
        total = first_part + second_part + third_part
        return HttpResponse(total)
    except Publication.DoesNotExist:
        return wcode.goerror(request, ["This is publication not found!"])


def get_publ_manager(request, id):
    """Запускает страницу управления конспектом"""

    try:
        # Получаем пользователя
        user_data = check_auth(request)

        # Получаем конспект, который хотим управлять
        _publication = Publication.objects.get(id_publication=id)

        # Проверяем, является ли автором этого конспекта тот пользователь
        # Который захотел управлять этим конспектом
        current_id = get_user_id(request)
        if current_id == _publication.id_author:

            # Получаем список редакторов конспекта, а также черный список
            wp = WikiPermissions()
            wp.load_permissions(_publication.permissions)
            white_list = wp.get_white_list()
            black_list = wp.get_black_list()

            # Получаем путь к конспекту
            cur_user = User.objects.get(id_user=current_id)
            id_folder = int(_publication.tree_path.split(":")[1])
            wft = WikiFileTree()
            wft.load_tree(cur_user.file_tree)
            path_to_folder = wft.get_path_folder(id_folder)

            context = {
                "user_data": user_data,
                "user_id": current_id,
                "publication": _publication,
                "path_to_folder": path_to_folder,
                "white_list": white_list,
                "black_list": black_list,
                "notify": wcode.notify.instant.get(request)
            }
            return render(request, 'wiki/publ_manager.html', context)
        else:
            return wcode.goerror(request,
                                 ["Вы не являетесь автором данного конспекта, чтобы перейти в панель управления!"])

    except Publication.DoesNotExist:
        return wcode.goerror(request,
                             ["This is publication not found!", "Page not found: publ_manager/" + str(id) + "/"])
    except User.DoesNotExist:
        return wcode.goerror(request, ["User not found!"])
    except:
        return wcode.goerror(request, ["Ошибка перехода на страницу управления конспектом."])


@csrf_protect
def get_add_dynamic_comment(request, id):
    """Ajax представление. Добавление комментария."""

    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('no', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, добавляем динамический комментарий к теущему конспекту

            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)

                # Получаем комментарий, который хотим оставить
                dynamic_comment = request.POST.get('dynamic_comment')

                # Получаем номер абзаца, в котором оставил пользователь комментарий
                num_paragraph = request.POST.get('num_paragraph')

                # Получаем текущую дату
                date = str(datetime.datetime.now())
                date = date[:len(date) - 7]

                # Загружаем модуль комментариев
                wc = WikiComments()

                # Получаем текущую статистику
                stat = Statistics.objects.get(id_statistics=1)

                # Получаем текущего пользователя
                cur_user = User.objects.get(id_user=get_user_id(request))

                try:
                    # Получаем динамический параграф
                    dynamic_paragraph = DynamicParagraph.objects.get(publication=publication, paragraph=num_paragraph)
                    # Загружаем комментарии
                    wc.load_comments(dynamic_paragraph.comments)

                except DynamicParagraph.DoesNotExist:
                    # Если этот динамический параграф отсутствует, создаем его
                    wc.create_comments(id=stat.total_dynamic_comments + 1)
                    dynamic_paragraph = DynamicParagraph(publication=publication,
                                                         paragraph=num_paragraph,
                                                         comments=wc.get_xml_str())
                    stat.total_dynamic_comments += 1

                except User.DoesNotExist:
                    return wcode.goerror(request, ["User not found."])

                # Добавляем новый коммент в БД
                new_comment = Comment(id_comment=stat.total_comments + 1,
                                      id_author=cur_user.id_user,
                                      id_publication=publication.id_publication,
                                      date=date,
                                      text=dynamic_comment)

                # Добавляем новый комментарий в xml комментариев параграфа
                wc.create_comment(id_comment=stat.total_comments + 1,
                                  user_id=cur_user.id_user,
                                  text=dynamic_comment,
                                  user_name=cur_user.nickname,
                                  date=date,
                                  is_moderator=False)

                stat.total_comments += 1
                dynamic_paragraph.comments = wc.get_xml_str()

                dynamic_paragraph.save()
                stat.save()
                new_comment.save()

                return HttpResponse('ok', content_type='text/html')

            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


@csrf_protect
def get_reply_dynamic_comment(request, id):
    """Ajax представление. Добавление ответа на динамический комментария."""

    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('no', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, добавляем динамический комментарий к теущему конспекту

            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)

                # Получаем комментарий, который хотим оставить
                dynamic_comment = request.POST.get('comment')

                # Получаем id комментария, на который хотим ответить
                reply_comment_id = request.POST.get('reply_comment_id')

                # Получаем номер параграфа, где хранится этот комментарий
                num_paragraph = request.POST.get('num_paragraph')

                # Получаем текущую дату
                date = str(datetime.datetime.now())
                date = date[:len(date) - 7]

                # Загружаем модуль комментариев
                wc = WikiComments()

                # Получаем текущую статистику
                stat = Statistics.objects.get(id_statistics=1)

                # Получаем текущего пользователя
                cur_user = User.objects.get(id_user=get_user_id(request))

                try:
                    # Получаем динамический параграф
                    dynamic_paragraph = DynamicParagraph.objects.get(publication=publication, paragraph=num_paragraph)
                    # Загружаем комментарии
                    wc.load_comments(dynamic_paragraph.comments)

                    # Добавляем новый коммент в БД
                    new_comment = Comment(id_comment=stat.total_comments + 1,
                                          id_author=cur_user.id_user,
                                          id_publication=publication.id_publication,
                                          date=date,
                                          text=dynamic_comment)

                    # Добавляем новый комментарий в xml комментариев параграфа
                    wc.reply(new_id=stat.total_comments + 1,
                             user_id=cur_user.id_user,
                             user_name=cur_user.nickname,
                             text=dynamic_comment,
                             reply_id=reply_comment_id,
                             date=date,
                             is_moderator=False)

                    stat.total_comments += 1
                    dynamic_paragraph.comments = wc.get_xml_str()

                    dynamic_paragraph.save()
                    stat.save()
                    new_comment.save()

                    return HttpResponse('ok', content_type='text/html')

                except DynamicParagraph.DoesNotExist:
                    return wcode.goerror(request, ["DynamicParagraph not found."])
                except User.DoesNotExist:
                    return wcode.goerror(request, ["User not found."])

            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


@csrf_protect
def get_add_main_comment(request, id):
    """Ajax представление. Добавление общего комментария."""

    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('no', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, добавляем общий комментарий к текущему конспекту

            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)

                # Получаем пользователя, оставляющего комментарий
                current_user = User.objects.get(id_user=get_user_id(request))

                # Получаем комментарий, который хотим оставить
                main_comment = request.POST.get('main_comment')

                # Получаем id автора, которому нужно ответить
                reply_id = int(request.POST.get('reply_author_id'))

                # Загружаем имеющиеся комментарии у конспекта
                wiki_comments = WikiComments()
                wiki_comments.load_comments(publication.main_comments)

                # Узнаем количество комментариев
                stat = Statistics.objects.get(id_statistics=1)
                total_comments = stat.total_comments

                # Если комментарий не пустой
                if main_comment:

                    # Получаем текущую дату
                    date = str(datetime.datetime.now())
                    date = date[:len(date) - 7]

                    new_comment = Comment(id_comment=total_comments + 1,
                                          id_author=get_user_id(request),
                                          text=main_comment,
                                          id_publication=id,
                                          date=date)

                    # Повышаем у статистики количество созданных комментариев
                    stat.total_comments += 1

                    # Если пользователь создал новый комментарий, ни кому не ответив:
                    if reply_id == -1:
                        # Создаем новый комментарий в xml
                        wiki_comments.create_comment(id_comment=total_comments + 1,
                                                     user_id=get_user_id(request),
                                                     text=main_comment,
                                                     user_name=current_user.nickname,
                                                     date=date,
                                                     is_moderator=False)
                    else:
                        # Отвечаем на существующий комментарий
                        wiki_comments.reply(new_id=total_comments + 1,
                                            user_id=get_user_id(request),
                                            user_name=current_user.nickname,
                                            text=main_comment,
                                            reply_id=reply_id,
                                            date=date,
                                            is_moderator=False)

                    # Обновляем все комментарии в публикации
                    publication.main_comments = wiki_comments.get_xml_str()

                    # Сохраняем все изменения в БД
                    publication.save()
                    stat.save()
                    new_comment.save()

                    return HttpResponse('ok', content_type='text/html')
                else:
                    print("Пустой комментарий добавлять нельзя!")
                    return HttpResponse('no', content_type='text/html')

            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
            except User.DoesNotExist:
                return wcode.goerror(request, ["This is user not found!",
                                               "User not found: user/" + str(get_user_id(request)) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


@csrf_protect
def get_save_publication(request, id):
    """Ajax представление. Сохранение изменений в конспекте."""

    # Вспомогательный метод. Создает новую версию
    def create_new_version(md_paragraphs, publication):
        wiki_versions = WikiVersions()
        wiki_versions.load_versions(publication.versions)
        wiki_versions.new_version(publication.id_author, md_paragraphs)
        wiki_versions.set_head(wiki_versions.get_count_versions())
        new_text = ""
        for p in wiki_versions.get_head():
            new_text += p
        publication.text = new_text
        publication.versions = wiki_versions.get_archive()
        publication.save()

    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('no', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)
                # Получаем пользователя, оставляющего комментарий
                current_user = User.objects.get(id_user=get_user_id(request))
                # Получаем количество абзацев
                count_paragraphs = int(request.POST.get("count_paragraphs"))
                # Получаем абзацы
                md_text = ""
                for i in range(0, count_paragraphs):
                    md_text += request.POST.get(str(i + 1))
                wiki_markdown = WikiMarkdown()
                md_paragraphs = wiki_markdown.split(md_text)

                # Сверяем с теми, что есть на данный момент:
                current_paragraphs = wiki_markdown.split(publication.text)
                if len(current_paragraphs) == len(md_paragraphs):
                    equals = True
                    for i in range(0, len(current_paragraphs)):
                        if current_paragraphs[i] != md_paragraphs[i]:
                            equals = False
                            break
                    if equals:
                        return HttpResponse('eq', content_type='text/html')
                    else:
                        # Если версии не равны, порождаем новую.
                        create_new_version(md_paragraphs, publication)
                        return HttpResponse('not_eq', content_type='text/html')
                else:
                    # Порождаем новую версию
                    create_new_version(md_paragraphs, publication)
                    return HttpResponse('not_eq', content_type='text/html')

            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


@csrf_protect
def get_get_version(request, id):
    """ Ajax представление. Получение конкретной версии конспекта """

    if request.method == "GET":
        # Если пользователь аутентифицирован то, начинаем получать все изменения
        try:
            # Получаем текущую публикацию
            publication = Publication.objects.get(id_publication=id)
            # Получаем версию, которую нужно отобразить
            to_version = int(request.GET.get("to_version"))

            wiki_versions = WikiVersions()
            wiki_versions.load_versions(publication.versions)
            paragraphs = wiki_versions.get_version(to_version)

            context = {}

            for i in range(0, len(paragraphs)):
                context[str(i + 1)] = paragraphs[i]

            context["count"] = str(len(paragraphs))

            return HttpResponse(json.dumps(context), content_type="application/json")

        except Publication.DoesNotExist:
            return wcode.goerror(request, ["This is publication not found!",
                                           "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


@csrf_protect
def get_set_head(request, id):
    """ Ajax представление. становление выбранной версии как HEAD """

    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)
                # Получаем пользователя, оставляющего комментарий
                current_user = User.objects.get(id_user=get_user_id(request))
                # Получаем версию, которую необходимо сделать HEAD
                to_version = int(request.POST.get("to_version"))
                # Переключаем версию
                wiki_markdown = WikiMarkdown()
                wiki_versions = WikiVersions()
                wiki_versions.load_versions(publication.versions)
                wiki_versions.set_head(to_version)
                # Устанавливаем новое состояние версий
                publication.versions = wiki_versions.get_archive()
                # Получаем чисто текст текущей
                paragraphs = wiki_versions.get_head()
                md_text = ""
                for paragraph in paragraphs:
                    md_text += paragraph
                # Устанавливаем текущий текст конспекта
                publication.text = md_text
                # Сохраняем все изменения в БД
                publication.save()

                return HttpResponse('ok', content_type='text/html')
            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


def get_save_page(request, id):
    """ Сохранение конспекта в свое дерево конспектов """
    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)
                # Получаем пользователя, который собирается произвести сохранение конспекта
                current_user = User.objects.get(id_user=get_user_id(request))
                # Если этот пользователь не является автором данного конспекта:
                if current_user.id_user != publication.id_author:
                    # Получаем дерево конспектов пользователя
                    wft = WikiFileTree()
                    wft.load_tree(current_user.file_tree)
                    # Получаем папку, в которую необходимо сохранить конспект
                    save_folder = request.POST.get("save_folder")
                    try:
                        # Получаем id папки в которую собираемся сохранить конспект
                        id_folder = int(save_folder.strip(" \n\r\t").split(":")[1])

                        # Проверяем, существует ли такая папка:
                        Folder.objects.get(id_folder=id_folder)

                        # Проверяем, сохранил ли пользователь у себя уже этот конспект
                        if wft.is_publication(publication.id_publication):
                            wcode.notify.instant.create(request, 'error',
                                                        'Вы уже сохранили этот конспект у себя в дереве.')
                            return wcode.goto('/page/' + str(id))

                        # Если такая папка существует сохраняем в нее этот конспект
                        wft.create_publication(id=publication.id_publication,
                                               name=publication.title,
                                               access="public",
                                               type="saved",
                                               id_folder=id_folder)

                        publication.saves += 1
                        publication.stars += 1
                        current_user.file_tree = wft.get_xml_str()
                        current_user.save()
                        publication.save()

                        wcode.notify.instant.create(request, 'info', 'Конспект сохранен')
                        return wcode.goto('/page/' + str(id))
                    except Folder.DoesNotExist:
                        return wcode.goerror(request, ["Такой папки не существует"])
                    except:
                        return wcode.goerror(request, ["Передан неверный формат пути к папке"])

                else:
                    return wcode.goerror(request, ["Вы являетесь автором данного конспекта, "
                                                   "Вы не можете его сохранить!"])
            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


def get_add_star_publication(request, id):
    """ Добавление или удаление звезды у конспекта """
    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)
                # Получаем пользователя, который собирается добавить или убрать звезду
                current_user = User.objects.get(id_user=get_user_id(request))
                # Проверяем, ставил ли он уже звезду или нет
                try:
                    starring = Starring.objects.get(id_user=current_user.id_user, id_publ=publication.id_publication)

                    # Если звезда уже существует у этого пользователя, удаляем ее:
                    publication.stars -= 1
                    starring.delete()
                    publication.save()

                    return HttpResponse('ok', content_type='text/html')

                except Starring.DoesNotExist:
                    # Если пользователь, еще на ставил лайк, ставим

                    # Получаем текущую дату
                    date = str(datetime.datetime.now())
                    date = date[:len(date) - 7]

                    new_star = Starring(id_user=current_user.id_user,
                                        id_publ=publication.id_publication,
                                        date=date)

                    publication.stars += 1
                    new_star.save()
                    publication.save()

                    return HttpResponse('ok', content_type='text/html')

            except User.DoesNotExist:
                return wcode.goerror(request, ["User not found."])
            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return HttpResponse('no', content_type='text/html')


@csrf_exempt
def get_load_md(request, id):
    """ Загрузка конспекта в формате markdown """
    if request.method == "POST":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html; charset=utf8')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем текущую публикацию
                publication = Publication.objects.get(id_publication=id)

                response = StreamingHttpResponse(publication.text)
                response['Content-Type'] = 'text/plain; charset=utf8'
                return response

            except User.DoesNotExist:
                return wcode.goerror(request, ["User not found."])
            except Publication.DoesNotExist:
                return wcode.goerror(request, ["This is publication not found!",
                                               "Page not found: publ_manager/" + str(id) + "/"])
    else:
        return wcode.goerror(request, ["По техническим причинам, вы пока не можете скачать этот конспект."])


def get_get_path_to_folder(request):
    """ Получение полного пути к папке """
    if request.method == "GET":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html; charset=utf8')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем папку, к которой необходимо получить путь
                id_folder = int(request.GET.get('id_folder'))
                # Получаем пользователя
                cur_user = User.objects.get(id_user=get_user_id(request))

                # Получаем путь к папке
                wft = WikiFileTree()
                wft.load_tree(cur_user.file_tree)
                folder_path = wft.get_path_folder(id_folder)

                if folder_path is not None:
                    return HttpResponse(folder_path, content_type='text/html')
                else:
                    return HttpResponse('no', content_type='text/html')
            except User.DoesNotExist:
                return wcode.goerror(request, ["User not found."])
            except:
                return HttpResponse('no', content_type='text/html')
    else:
        return HttpResponse('no', content_type='text/html')


def get_get_path_to_publ(request, id):
    """ Получение полного пути к конспекту """
    if request.method == "GET":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html; charset=utf8')
        else:
            # Если пользователь аутентифицирован то, начинаем получать все изменения
            try:
                # Получаем конспект, к которой необходимо получить путь
                id_publ = int(request.GET.get('id_publ'))
                # Получаем пользователя
                cur_user = User.objects.get(id_user=get_user_id(request))

                # Получаем путь к конспекту
                wft = WikiFileTree()
                wft.load_tree(cur_user.file_tree)
                publ_path = wft.get_path_publ(id_publ)

                if publ_path is not None:
                    return HttpResponse(publ_path, content_type='text/html')
                else:
                    return HttpResponse('no', content_type='text/html')
            except User.DoesNotExist:
                return wcode.goerror(request, ["User not found."])
            except:
                return HttpResponse('no', content_type='text/html')
    else:
        return HttpResponse('no', content_type='text/html')


def get_comment_rating_up(request, id):
    """ Повышение рейтинга у комментария """
    if request.method == "GET":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html; charset=utf8')
        else:
            try:
                # Получаем id комментария
                id_comment = int(request.GET.get('id_comment'))
                # Получаем пользователя
                cur_user = User.objects.get(id_user=get_user_id(request))
                # Получаем id конспекта
                publication = Publication.objects.get(id_publication=id)
                # Получаем сам комментарий
                cur_comment = Comment.objects.get(id_comment=id_comment)
                # Проверяем, был ли уже установлен дизлайк или лайк
                try:
                    comment_rating = CommentRating.objects.get(id_user=cur_user.id_user, id_comment=id_comment)
                except CommentRating.DoesNotExist:
                    comment_rating = CommentRating(id_user=cur_user.id_user,
                                                   id_user_to=cur_comment.id_author,
                                                   id_comment=id_comment,
                                                   type="none")

                # Получаем место где лежит комментарий (main/dynamic)
                location = request.GET.get('location')

                result = "no"

                if location == "main":
                    # Получаем комментарий в конспекте
                    wc = WikiComments()
                    wc.load_comments(publication.main_comments)

                    # Проверяем на "самолайк"
                    if wc.get_user_id(id_comment) == cur_user.id_user:
                        return HttpResponse('no', content_type='text/html')

                    if comment_rating.type == "none":
                        wc.up_rating(id_comment)
                        comment_rating.type = "up"
                        result = "up"
                    elif comment_rating.type == "up":
                        result = "none"
                    elif comment_rating.type == "down":
                        wc.up_rating(id_comment)
                        comment_rating.type = "none"
                        result = "up"

                    publication.main_comments = wc.get_xml_str()
                    publication.save()
                    comment_rating.save()

                    return HttpResponse(result, content_type='text/html')

                elif location == "dynamic":

                    num_paragraph = request.GET.get('selected_num_paragraph')
                    # Ищем комментарий в динамических абзацах конспекта
                    dynamic_comment = DynamicParagraph.objects.get(publication=publication, paragraph=num_paragraph)

                    # Получаем комментарий в конспекте
                    wc = WikiComments()
                    wc.load_comments(dynamic_comment.comments)

                    # Проверяем на "самолайк"
                    if wc.get_user_id(id_comment) == cur_user.id_user:
                        return HttpResponse('no', content_type='text/html')

                    if comment_rating.type == "none":
                        wc.up_rating(id_comment)
                        comment_rating.type = "up"
                        result = "up"
                    elif comment_rating.type == "up":
                        result = "none"
                    elif comment_rating.type == "down":
                        wc.up_rating(id_comment)
                        comment_rating.type = "none"
                        result = "up"

                    dynamic_comment.comments = wc.get_xml_str()
                    dynamic_comment.save()
                    publication.save()
                    comment_rating.save()

                    return HttpResponse(result, content_type='text/html')
                else:
                    return HttpResponse('no', content_type='text/html')

            except User.DoesNotExist:
                return wcode.goerror(request, ["User not found."])
            except Publication.DoesNotExist:
                return wcode.goerror(request, ["Publication not found."])
            except Comment.DoesNotExist:
                return wcode.goerror(request, ["Comment not found."])
    else:
        return HttpResponse('no', content_type='text/html')


def get_comment_rating_down(request, id):
    """ Повышение рейтинга у комментария """
    if request.method == "GET":
        # Проверяем, аутентифицирован ли пользователь
        if get_user_id(request) == -1:
            return HttpResponse('auth', content_type='text/html; charset=utf8')
        else:
            try:
                # Получаем id комментария
                id_comment = int(request.GET.get('id_comment'))
                # Получаем пользователя
                cur_user = User.objects.get(id_user=get_user_id(request))
                # Получаем id конспекта
                publication = Publication.objects.get(id_publication=id)
                # Получаем сам комментарий
                cur_comment = Comment.objects.get(id_comment=id_comment)
                # Проверяем, был ли уже установлен дизлайк или лайк
                try:
                    comment_rating = CommentRating.objects.get(id_user=cur_user.id_user, id_comment=id_comment)
                except CommentRating.DoesNotExist:
                    comment_rating = CommentRating(id_user=cur_user.id_user,
                                                   id_user_to=cur_comment.id_author,
                                                   id_comment=id_comment,
                                                   type="none")

                # Получаем место где лежит комментарий (main/dynamic)
                location = request.GET.get('location')

                result = "no"

                if location == "main":
                    # Получаем комментарий в конспекте
                    wc = WikiComments()
                    wc.load_comments(publication.main_comments)

                    # Проверяем на "самодизлайк"
                    if wc.get_user_id(id_comment) == cur_user.id_user:
                        return HttpResponse('no', content_type='text/html')

                    if comment_rating.type == "none":
                        wc.down_rating(id_comment)
                        comment_rating.type = "down"
                        result = "down"
                    elif comment_rating.type == "down":
                        result = "none"
                    elif comment_rating.type == "up":
                        wc.down_rating(id_comment)
                        comment_rating.type = "none"
                        result = "down"

                    publication.main_comments = wc.get_xml_str()
                    publication.save()
                    comment_rating.save()

                    return HttpResponse(result, content_type='text/html')

                elif location == "dynamic":

                    num_paragraph = request.GET.get('selected_num_paragraph')
                    # Ищем комментарий в динамических абзацах конспекта
                    dynamic_comment = DynamicParagraph.objects.get(publication=publication, paragraph=num_paragraph)

                    # Получаем комментарий в конспекте
                    wc = WikiComments()
                    wc.load_comments(dynamic_comment.comments)

                    # Проверяем на "самодизлайк"
                    if wc.get_user_id(id_comment) == cur_user.id_user:
                        return HttpResponse('no', content_type='text/html')

                    if comment_rating.type == "none":
                        wc.down_rating(id_comment)
                        comment_rating.type = "down"
                        result = "down"
                    elif comment_rating.type == "down":
                        result = "none"
                    elif comment_rating.type == "up":
                        wc.down_rating(id_comment)
                        comment_rating.type = "none"
                        result = "down"

                    dynamic_comment.comments = wc.get_xml_str()
                    dynamic_comment.save()
                    publication.save()
                    comment_rating.save()

                    return HttpResponse(result, content_type='text/html')
                else:
                    return HttpResponse('no', content_type='text/html')

            except User.DoesNotExist:
                return wcode.goerror(request, ["User not found."])
            except Publication.DoesNotExist:
                return wcode.goerror(request, ["Publication not found."])
            except DynamicParagraph.DoesNotExist:
                return wcode.goerror(request, ["DynamicParagraph not found."])
            except Comment.DoesNotExist:
                return wcode.goerror(request, ["Comment not found."])
    else:
        return HttpResponse('no', content_type='text/html')
