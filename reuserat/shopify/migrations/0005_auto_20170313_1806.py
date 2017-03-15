# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 18:06
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0004_auto_20170312_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemorderdetails',
            name='charge_id',
            field=models.CharField(default=2, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemorderdetails',
            name='order_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemorderdetails',
            name='transfer_id',
            field=models.IntegerField(default=34),
            preserve_default=False,
        ),
    ]
