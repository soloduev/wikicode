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

from django.shortcuts import render

from WikiCode.apps.wiki.models import User, Notification
from WikiCode.apps.wiki.src.views.error_view import get_error_page
from WikiCode.apps.wiki.src.modules.wiki_tree.wiki_tree import WikiFileTree
from WikiCode.apps.wiki.src.modules.notify_generator.wiki_notify import WikiNotify
from WikiCode.apps.wiki.views import user_view
from .auth import check_auth, get_user_id


def get_notifications(request, notify=None):
    """ Возвращает страницу уведомлений.
        Может принимать notify(сообщение, которое можно вывести после отображения страницы):
        notify:
            {
                'type': 'error|info',
                'text': 'any text',
            }
        """
    if notify is None:
        notify = {'type': 'msg', 'text': ''}

    user_data = check_auth(request)
    try:
        user = User.objects.get(email=user_data)
        wft = WikiFileTree()
        wft.load_tree(user.file_tree)

        try:
            all_notifications = Notification.objects.filter(id_addressee=user.id_user)
            notifications = []
            total_notifies = 1
            for notification in reversed(all_notifications):
                try:
                    sender = User.objects.get(id_user=notification.id_sender)
                    notifications.append({
                        "id_notification": notification.id_notification,
                        "title": notification.title,
                        "id_sender": notification.id_sender,
                        "id_addressee": notification.id_addressee,
                        "is_read": notification.is_read,
                        "date": notification.date,
                        "html_text": notification.html_text,
                        "sender_nickname": sender.nickname,
                        "id_notify": str(total_notifies),
                        "type": notification.type
                    })
                    total_notifies += 1
                except User.DoesNotExist:
                    pass
        except Notification.DoesNotExist:
            notifications = None

        user_id = get_user_id(request)
        context = {
            "user_data": user_data,
            "user_id": user_id,
            "preview_tree": wft.to_html_preview(),
            "notifications": notifications,
            "notify": notify
        }

        return render(request, 'wiki/notifications.html', context)
    except User.DoesNotExist:
        return get_error_page(request, ["Sorry, user is not defined!", "Page not found: 'user/" + str(id) + "/'"])


def get_send_request_colleagues(request, id):
    if request.method == "POST":

        try:
            # Получаем id отправителя и получателя
            current_user = User.objects.get(id_user=get_user_id(request))
            send_user = User.objects.get(id_user=id)

            # Получаем текущую дату
            date = str(datetime.datetime.now())
            date = date[:len(date) - 7]

            # Генериуем html уведомления
            html_text = WikiNotify.generate_add_colleague(author_nickname=current_user.nickname,
                                                          author_email=current_user.email,
                                                          author_id=current_user.id_user,
                                                          author_text="")

            new_notify = Notification(id_notification=Notification.objects.count() + 1,
                                      title="Заявка в коллеги",
                                      type="add_colleague",
                                      id_sender=current_user.id_user,
                                      id_addressee=send_user.id_user,
                                      is_read=False,
                                      date=date,
                                      html_text=html_text)

            new_notify.save()

            return user_view.get_user(request,
                                      id,
                                      notify={'type': 'info',
                                              'text': 'Заявка на добавление в коллеги успешно отправлена.\n\n'})
        except User.DoesNotExist:
            return get_error_page(request, ["User mot found!"])
    else:
        return get_error_page(request, ["Sorry, could not send the request to add the college for technical reasons!"])
