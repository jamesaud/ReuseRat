# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-05 01:47
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0006_remove_paypalaccount_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripeaccount',
            name='account_holder_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='stripeaccount',
            name='account_number_last_four',
            field=models.CharField(max_length=4, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Has to be 4 integers', regex='^\\d{4}$')]),
        ),
        migrations.AlterField(
            model_name='stripeaccount',
            name='account_number_length',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='stripeaccount',
            name='routing_number_last_four',
            field=models.CharField(max_length=4, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Has to be 4 integers', regex='^\\d{4}$')]),
        ),
    ]
