# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-02-18 14:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0082_merge_20190215_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobRuntimeOpenStack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_name', models.CharField(help_text='Name of the VM Image to launch', max_length=255)),
                ('cwl_base_command', models.TextField(help_text="JSON-encoded command array to run the  image's installed CWL engine")),
                ('cwl_post_process_command', models.TextField(blank=True, help_text='JSON-encoded command array to run after workflow completes')),
                ('cwl_pre_process_command', models.TextField(blank=True, help_text='JSON-encoded command array to run before cwl_base_command')),
                ('cloud_settings', models.ForeignKey(help_text='Cloud settings ', on_delete=django.db.models.deletion.CASCADE, to='data.CloudSettings')),
            ],
        ),
        migrations.AddField(
            model_name='jobsettings',
            name='lando_connection',
            field=models.ForeignKey(help_text='Lando connection to use for this job settings', null=True, on_delete=django.db.models.deletion.CASCADE, to='data.LandoConnection'),
        ),
        migrations.AlterField(
            model_name='jobflavor',
            name='memory',
            field=models.CharField(default='1Gi', help_text='How much memory in k8s units to be use when running a job with this flavor', max_length=12),
        ),
        migrations.CreateModel(
            name='JobRuntimeStepK8s',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_type', models.CharField(choices=[('stage_data', 'Stage Data'), ('run_workflow', 'Run Workflow'), ('organize_output', 'Organize Output'), ('save_output', 'Save Output'), ('record_output_project', 'Record Output Project')], max_length=255)),
                ('image_name', models.CharField(help_text='Name of the image to run for this step', max_length=255)),
                ('flavor', models.ForeignKey(help_text='Cpu/Memory to use when running this step', on_delete=django.db.models.deletion.CASCADE, to='data.JobFlavor')),
                ('base_command',
                 django.contrib.postgres.fields.jsonb.JSONField(help_text='JSON array with base command to run')),
            ],
        ),

        migrations.CreateModel(
            name='JobRuntimeK8s',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('steps', models.ManyToManyField(help_text='Steps to be used by this job runtime', to='data.JobRuntimeStepK8s'))
            ],
        ),
        migrations.AddField(
            model_name='landoconnection',
            name='cluster_type',
            field=models.CharField(choices=[('vm', 'OpenStack Cluster Type'), ('k8s', 'K8s Cluster Type')], default='vm',
                                   max_length=255),
        ),
        migrations.AddField(
            model_name='jobsettings',
            name='job_runtime_k8s',
            field=models.ForeignKey(blank=True, help_text='K8s command set to use for type k8s', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, to='data.JobRuntimeK8s'),
        ),
        migrations.AddField(
            model_name='jobsettings',
            name='job_runtime_openstack',
            field=models.ForeignKey(blank=True, help_text='VM command to use for type vm', null=True,
                                    on_delete=django.db.models.deletion.CASCADE, to='data.JobRuntimeOpenStack'),
        ),
    ]
