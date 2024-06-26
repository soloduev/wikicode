/*
 Copyright (C) 2016 Igor Soloduev <diahorver@gmail.com>

 This file is part of WikiCode.

 WikiCode is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 WikiCode is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with WikiCode.  If not, see <http://www.gnu.org/licenses/>.
 */



/**
 * Created by lazytroll on 24.04.16.
 */



//Лайк пользователя
$("#wiki-code-like-user").click(function () {
    $.ajax({
        type: "POST",
        url: "like_user/",
        data:{
            'data':'',
        },
        dataType: "text",
        cache: false,
        success: function(data){
            if (data == 'ok'){
                location.reload();
            }
            else
            {
                //Говорим, что лайкнуть не удалось(
            }
        }
    });
});


//Лайк пользователя c другой кнопки
$("#wiki-code-like-user-link").click(function () {
    $.ajax({
        type: "POST",
        url: "like_user/",
        data:{
            'data':'',
        },
        dataType: "text",
        cache: false,
        success: function(data){
            if (data == 'ok'){
                location.reload();
            }
            else
            {
                //Говорим, что лайкнуть не удалось(
            }
        }
    });
});

//Отправка заявки в коллеги
$("#wiki-style-btn-user-add-colleague").click(function () {
    $.ajax({
        type: "POST",
        url: "user_send_request_for_colleagues/",
        data:{
            'nickname':''+$("#nickname_for_add_colleagues").val(),
        },
        dataType: "text",
        cache: false,
        success: function(data){
            if (data == 'ok'){
                location.reload();
            }
        }
    });
});

//Отправка письма
$("#wiki-send-message").click(function () {
    if ($("#input_wiki_message").val().length > 10) {
        $.ajax({
            type: "POST",
            url: "user_send_message/",
            data: {
                'message': '' + $("#input_wiki_message").val(),
            },
            dataType: "text",
            cache: false,
            success: function (data) {
                if (data == 'ok') {
                    location.reload();
                }
            }
        });
    }
    else
    {
        console.log("Письмо должно содержать более 10 символов");
    }
});
