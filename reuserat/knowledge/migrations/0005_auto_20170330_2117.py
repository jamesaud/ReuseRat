# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-30 21:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0004_auto_20170330_2113'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='faq',
            options={'ordering': ('-priority',)},
        ),
        migrations.AlterModelOptions(
            name='faqcategory',
            options={'ordering': ('-priority',)},
        ),
    ]