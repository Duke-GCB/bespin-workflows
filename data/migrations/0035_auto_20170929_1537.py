# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-09-29 15:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0034_auto_20170928_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmessage',
            name='bcc_email',
            field=models.TextField(blank=True, help_text='space-separated Email addresses to bcc', null=True),
        ),
    ]
