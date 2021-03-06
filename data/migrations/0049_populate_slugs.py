# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-06-12 13:54
from __future__ import unicode_literals

from django.db import migrations
from django.template.defaultfilters import slugify


def populate_workflow_slugs(apps, schema_editor):
    Workflow = apps.get_model("data", "Workflow")
    for workflow in Workflow.objects.all():
        workflow.slug = slugify(workflow.name)
        workflow.save()


def populate_job_questionnaire_types(apps, schema_editor):
    JobQuestionnaire = apps.get_model("data", "JobQuestionnaire")
    JobQuestionnaireType = apps.get_model("data", "JobQuestionnaireType")
    generic_type, _ = JobQuestionnaireType.objects.get_or_create(slug='generic')
    for job_questionnaire in JobQuestionnaire.objects.all():
        job_questionnaire.type = generic_type
        job_questionnaire.save()


def reverse_populate_job_questionnaire_types(apps, schema_editor):
    JobQuestionnaire = apps.get_model("data", "JobQuestionnaire")
    JobQuestionnaireType = apps.get_model("data", "JobQuestionnaireType")
    for job_questionnaire in JobQuestionnaire.objects.all():
        job_questionnaire.type = None
        job_questionnaire.save()
    try:
        generic_type = JobQuestionnaireType.objects.get(slug='generic')
        generic_type.delete()
    except JobQuestionnaireType.DoesNotExist:
        pass  # Don't need to delete it


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0048_auto_20180612_1351'),
    ]

    operations = [
        migrations.RunPython(populate_workflow_slugs, migrations.RunPython.noop),
        migrations.RunPython(populate_job_questionnaire_types, reverse_populate_job_questionnaire_types),
    ]
