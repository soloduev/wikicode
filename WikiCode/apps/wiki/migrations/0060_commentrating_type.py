# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-01-14 20:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0059_auto_20170114_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentrating',
            name='type',
            field=models.BooleanField(default=None),
            preserve_default=False,
        ),
    ]
