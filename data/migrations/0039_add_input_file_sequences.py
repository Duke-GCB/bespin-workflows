# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-12-12 16:49
from __future__ import unicode_literals

from django.db import migrations, models

def populate_sequence_fields(apps, schema_editor):
    populate_sequence_for_model(apps.get_model('data', 'DDSJobInputFile'))
    populate_sequence_for_model(apps.get_model('data', 'URLJobInputFile'))


def populate_sequence_for_model(model):
    # Fill in sequence_group and sequence with numbers so we can get a baseline of sorting.
    for input_file in model.objects.all():
        input_file.sequence_group = 0
        input_file.sequence = input_file.id
        input_file.save()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0038_auto_20171106_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='ddsjobinputfile',
            name='sequence',
            field=models.IntegerField(help_text='Determines order within the sequence_group', null=True),
        ),
        migrations.AddField(
            model_name='ddsjobinputfile',
            name='sequence_group',
            field=models.IntegerField(help_text='Determines group(questionnaire field) sequence within the job', null=True),
        ),
        migrations.AddField(
            model_name='urljobinputfile',
            name='sequence',
            field=models.IntegerField(help_text='Determines order within the sequence_group', null=True),
        ),
        migrations.AddField(
            model_name='urljobinputfile',
            name='sequence_group',
            field=models.IntegerField(help_text='Determines group(questionnaire field) sequence within the job', null=True),
        ),
        migrations.RunPython(populate_sequence_fields),
        migrations.AlterUniqueTogether(
            name='ddsjobinputfile',
            unique_together=set([('stage_group', 'sequence_group', 'sequence')]),
        ),
        migrations.AlterUniqueTogether(
            name='urljobinputfile',
            unique_together=set([('stage_group', 'sequence_group', 'sequence')]),
        ),
    ]
