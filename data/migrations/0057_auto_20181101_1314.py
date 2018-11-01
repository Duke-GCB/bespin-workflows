# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-11-01 13:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0056_auto_20180927_1928'),
    ]

    operations = [
        migrations.CreateModel(
            name='VMStrategy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Short user facing name', max_length=255)),
                ('volume_size_base', models.IntegerField(default=100, help_text='Base size in GB of for determining job volume size')),
                ('volume_size_factor', models.IntegerField(default=0, help_text='Number multiplied by total staged data size for determining job volume size')),
                ('volume_mounts', models.TextField(default='{"/dev/vdb1": "/work"}', help_text='JSON-encoded dictionary of volume mounts, e.g. {"/dev/vdb1": "/work"}')),
                ('vm_flavor', models.ForeignKey(help_text='VM Flavor to use when creating VM instances for this questionnaire', on_delete=django.db.models.deletion.CASCADE, to='data.VMFlavor')),
                ('vm_settings', models.ForeignKey(help_text='Collection of settings to use when launching job VMs for this questionnaire', on_delete=django.db.models.deletion.CASCADE, to='data.VMSettings')),
            ],
            options={
                'verbose_name_plural': 'VM Strategies',
            },
        ),
        migrations.CreateModel(
            name='WorkflowConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(help_text='Short user facing name', max_length=255)),
                ('system_job_order_json', models.TextField(help_text='JSON containing the portion of the job order specified by system.')),
                ('default_vm_strategy', models.ForeignKey(help_text='VM setup to use for jobs created with this configuration', on_delete=django.db.models.deletion.CASCADE, to='data.VMStrategy')),
                ('share_group', models.ForeignKey(help_text='Users who will have job output shared with them', on_delete=django.db.models.deletion.CASCADE, to='data.ShareGroup')),
            ],
        ),
        migrations.AddField(
            model_name='workflowversion',
            name='fields_json',
            field=models.TextField(blank=True, help_text='JSON containing the array of fields required by this workflow.'),
        ),
        migrations.AddField(
            model_name='workflowconfiguration',
            name='workflow_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.WorkflowVersion'),
        ),
        migrations.AlterUniqueTogether(
            name='workflowconfiguration',
            unique_together=set([('workflow_version', 'name')]),
        ),
    ]