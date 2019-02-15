# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-01-24 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0074_auto_20190124_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='step',
            field=models.CharField(blank=True, choices=[('V', 'Create VM'), ('S', 'Staging In'), ('R', 'Running Workflow'), ('o', 'Organize Output Project'), ('O', 'Store Job Output'), ('P', 'Record Output Project'), ('T', 'Terminate VM')], help_text='Job step (progress within Running state)', max_length=1),
        ),
        migrations.AlterField(
            model_name='jobactivity',
            name='step',
            field=models.CharField(blank=True, choices=[('V', 'Create VM'), ('S', 'Staging In'), ('R', 'Running Workflow'), ('o', 'Organize Output Project'), ('O', 'Store Job Output'), ('P', 'Record Output Project'), ('T', 'Terminate VM')], help_text='Job step (progress within Running state)', max_length=1),
        ),
        migrations.AlterField(
            model_name='joberror',
            name='job_step',
            field=models.CharField(choices=[('V', 'Create VM'), ('S', 'Staging In'), ('R', 'Running Workflow'), ('o', 'Organize Output Project'), ('O', 'Store Job Output'), ('P', 'Record Output Project'), ('T', 'Terminate VM')], max_length=1),
        ),
    ]