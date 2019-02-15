# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-02-15 13:50
from __future__ import unicode_literals

from django.db import migrations


def populate_vm_command(apps, schema_editor):
    VMCommand = apps.get_model("data", "VMCommand")
    JobSettings = apps.get_model("data", "JobSettings")
    for job_settings in JobSettings.objects.all():
        VMCommand.objects.create(
            job_settings=job_settings,
            cloud_settings=job_settings.cloud_settings,
            image_name=job_settings.image_name,
            cwl_base_command=job_settings.cwl_base_command,
            cwl_post_process_command=job_settings.cwl_post_process_command,
            cwl_pre_process_command=job_settings.cwl_pre_process_command,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0079_auto_20190215_1348'),
    ]

    operations = [
        migrations.RunPython(populate_vm_command, migrations.RunPython.noop),
    ]
