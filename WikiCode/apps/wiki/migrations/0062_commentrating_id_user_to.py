# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-01-14 21:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0061_auto_20170114_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentrating',
            name='id_user_to',
            field=models.BigIntegerField(default=-1),
            preserve_default=False,
        ),
    ]
