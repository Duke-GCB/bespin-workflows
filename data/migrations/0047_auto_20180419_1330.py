# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-04-19 13:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0046_auto_20180418_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='run_token',
            field=models.OneToOneField(blank=True, help_text='Token that allows permission for a job to be run', null=True, on_delete=django.db.models.deletion.CASCADE, to='data.JobToken'),
        ),
    ]
