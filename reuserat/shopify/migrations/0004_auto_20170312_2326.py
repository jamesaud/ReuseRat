# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-12 23:26
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0003_item_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemOrderDetails',
            fields=[
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shopify.Item')),
                ('charge_id', models.CharField(max_length=200, null=True)),
                ('transfer_id', models.IntegerField(null=True)),
                ('order_data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='item',
            name='status',
            field=models.CharField(choices=[('NOT_SOLD', 'Not Sold'), ('SOLD', 'Sold')], default='NOT_SOLD', max_length=100),
        ),
    ]