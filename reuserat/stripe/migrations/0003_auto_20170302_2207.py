# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 22:07
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0002_auto_20170302_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripeaccount',
            name='account_number_last_four',
            field=models.IntegerField(validators=django.core.validators.MinLengthValidator(4)),
        ),
        migrations.AlterField(
            model_name='stripeaccount',
            name='routing_number_last_four',
            field=models.IntegerField(validators=django.core.validators.MinLengthValidator(4)),
        ),
    ]
