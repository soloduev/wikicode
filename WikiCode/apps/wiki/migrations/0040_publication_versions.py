# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-11-07 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0039_auto_20160925_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='versions',
            field=models.BinaryField(blank=True),
        ),
    ]
