# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 02:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0005_auto_20170313_1806'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemorderdetails',
            name='charge_id',
        ),
        migrations.AlterField(
            model_name='itemorderdetails',
            name='transfer_id',
            field=models.CharField(max_length=100),
        ),
    ]