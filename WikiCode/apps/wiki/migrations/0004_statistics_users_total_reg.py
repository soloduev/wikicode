# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-03 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_comment_notification_publication_statistics_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='users_total_reg',
            field=models.BigIntegerField(default=0),
        ),
    ]
