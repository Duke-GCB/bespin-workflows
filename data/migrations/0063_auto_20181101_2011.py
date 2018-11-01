# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-11-01 20:11
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0062_prevent_null_json_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vmsettings',
            name='cwl_base_command',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[], help_text="Command array to run the  image's installed CWL engine"),
        ),
        migrations.AlterField(
            model_name='vmsettings',
            name='cwl_post_process_command',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[], help_text='Command array to run after workflow completes'),
        ),
        migrations.AlterField(
            model_name='vmsettings',
            name='cwl_pre_process_command',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[], help_text='Command array to run before cwl_base_command'),
        ),
    ]