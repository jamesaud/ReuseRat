# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-30 21:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0002_auto_20170307_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='priority',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='faqcategory',
            name='priority',
            field=models.IntegerField(default=100),
        ),
    ]