# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 21:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0002_email_max_length'),
        ('stripe', '0004_auto_20170302_2213'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaypalAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.EmailAddress')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
