# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-06-14 17:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_auto_20170614_1737'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobquestionnaire',
            old_name='system_job_order',
            new_name='system_job_order_json',
        ),
    ]
