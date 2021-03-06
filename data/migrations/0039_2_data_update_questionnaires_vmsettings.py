# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-12-08 18:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def update_questionnaires(apps, schema_editor):
    """
    Forward migration function to normalize settings into VMSettings and CloudSettings models
    :param apps: Django apps
    :param schema_editor: unused
    :return: None
    """
    VMSettings = apps.get_model("data", "VMSettings")
    CloudSettings = apps.get_model("data", "CloudSettings")
    JobQuestionnaire = apps.get_model("data", "JobQuestionnaire")
    Job = apps.get_model("data", "Job")
    for q in JobQuestionnaire.objects.all():
        # Create a cloud settings object with the VM project from the questionnaire.
        # Object initially just has the project name as its name
        cloud_settings, _ = CloudSettings.objects.get_or_create(name=q.vm_project.name, vm_project=q.vm_project)
        vm_settings, _ = VMSettings.objects.get_or_create(name=q.vm_project.name, cloud_settings=cloud_settings)
        q.vm_settings = vm_settings
        q.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0039_1_schema_add_questionnare_vmsettings'),
    ]

    operations = [
        # Populate VMSettings and CloudSettings objects from JobQuesetionnaire
        migrations.RunPython(update_questionnaires),
    ]
