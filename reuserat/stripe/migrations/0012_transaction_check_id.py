# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-30 18:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0011_auto_20170323_2356'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='check_id',
            field=models.CharField(default=2, max_length=255),
            preserve_default=False,
        ),
    ]
