# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-12-08 18:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0039_4_data_update_jobs_vmsettings'),
    ]

    operations = [
        # Remove the nullable value
        migrations.AlterField(
            model_name='job',
            name='vm_settings',
            field=models.ForeignKey(help_text='Collection of settings to use when launching VM for this job',
                                    null=False,
                                    on_delete=django.db.models.deletion.CASCADE, to='data.VMSettings'),
        ),

        # Remove the nullable value
        migrations.AlterField(
            model_name='job',
            name='vm_flavor',
            field=models.ForeignKey(help_text='VM Flavor to use when creating VM instances for this questionnaire',
                                    null=False,
                                    on_delete=django.db.models.deletion.CASCADE, to='data.VMFlavor'),
        ),

        # Remove the renamed vm_flavor_name field
        migrations.RemoveField(
            model_name='job',
            name='vm_flavor_name',
        ),

        migrations.RemoveField(
            model_name='job',
            name='vm_project_name',
        ),
    ]
