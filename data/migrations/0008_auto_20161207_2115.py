# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-07 21:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20161207_2114'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LandoSetting',
            new_name='LandoConnection',
        ),
    ]