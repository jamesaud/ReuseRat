# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-23 23:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0010_auto_20170323_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='amount_paid',
            new_name='amount',
        ),
    ]
