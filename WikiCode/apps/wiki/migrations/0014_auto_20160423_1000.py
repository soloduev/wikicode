# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-23 10:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0013_comment_num_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_position', models.BigIntegerField()),
                ('id_author', models.BigIntegerField()),
                ('nickname_author', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('data', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DynamicCommentParagraph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_position', models.BigIntegerField()),
                ('is_comment', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Paragraphs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_publication', models.BigIntegerField()),
                ('last_id', models.BigIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='dynamiccommentparagraph',
            name='paragraphs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.Paragraphs'),
        ),
        migrations.AddField(
            model_name='dynamiccomment',
            name='dynamic_comment_paragraph',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.DynamicCommentParagraph'),
        ),
    ]
