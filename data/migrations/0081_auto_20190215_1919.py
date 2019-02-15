# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-02-15 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0080_auto_20190215_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_settings',
            field=models.ForeignKey(help_text='Settings to use when running workflows on VMs or k8s Jobs', on_delete=django.db.models.deletion.CASCADE, to='data.JobSettings'),
        ),
        migrations.AlterField(
            model_name='jobquestionnaire',
            name='job_settings',
            field=models.ForeignKey(help_text='Settings to use when running workflows on VMs or k8s Jobs', on_delete=django.db.models.deletion.CASCADE, to='data.JobSettings'),
        ),
        migrations.AlterField(
            model_name='vmstrategy',
            name='job_settings',
            field=models.ForeignKey(help_text='Settings to use when running workflows on VMs or k8s Jobs for this questionnaire', on_delete=django.db.models.deletion.CASCADE, to='data.JobSettings'),
        ),
    ]
