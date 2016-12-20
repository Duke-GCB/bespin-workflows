# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-14 20:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20161214_2038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='joberror',
            name='state',
        ),
        migrations.AddField(
            model_name='joberror',
            name='job_stage',
            field=models.CharField(choices=[('V', 'Create VM'), ('S', 'Staging In'), ('R', 'Running Workflow'), ('O', 'Store Job Output'), ('T', 'Terminate VM')], default='V', max_length=1),
            preserve_default=False,
        ),
    ]