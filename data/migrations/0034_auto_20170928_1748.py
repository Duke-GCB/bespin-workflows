# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-09-28 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0033_emailmessage_emailtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='bcc_email',
            field=models.EmailField(blank=True, help_text='Email address to bcc', max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='body',
            field=models.TextField(help_text='Text of the message body'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='sender_email',
            field=models.EmailField(help_text='Email address of the sender', max_length=254),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='subject',
            field=models.TextField(help_text='Text of the message subject'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='to_email',
            field=models.EmailField(help_text='Email address of the recipient', max_length=254),
        ),
    ]
