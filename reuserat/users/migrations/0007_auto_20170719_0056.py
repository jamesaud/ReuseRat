# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-19 00:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20170719_0024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='birth_date',
        ),
        migrations.RemoveField(
            model_name='user',
            name='ssn_last_four',
        ),
    ]
