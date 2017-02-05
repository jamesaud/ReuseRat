# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 19:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import reuserat.address.models
import reuserat.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20170204_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address_apartment',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Apartment #'),
        ),
        migrations.AlterField(
            model_name='user',
            name='address',
            field=reuserat.address.models.AddressField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='address.Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=15, null=True, validators=[reuserat.users.models.phone_validator]),
        ),
    ]