# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-15 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0008_publication_nickname_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='downloads',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
    ]