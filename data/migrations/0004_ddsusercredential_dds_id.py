# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-19 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20170418_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='ddsusercredential',
            name='dds_id',
            field=models.CharField(default='', max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
