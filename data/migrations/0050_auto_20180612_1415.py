# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-06-12 14:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0049_populate_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobquestionnaire',
            name='type',
            field=models.ForeignKey(help_text='Type of questionnaire', on_delete=django.db.models.deletion.CASCADE, to='data.JobQuestionnaireType'),
        ),
        migrations.AlterField(
            model_name='jobquestionnairetype',
            name='slug',
            field=models.SlugField(help_text='Unique slug for specifying a questionnaire for a workflow version', unique=True),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='slug',
            field=models.SlugField(help_text='Unique slug to represent this workflow', unique=True),
        ),
    ]
