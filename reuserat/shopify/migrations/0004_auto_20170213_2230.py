# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify', '0003_auto_20170208_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='id',
            field=models.CharField(serialize=False, primary_key=True, max_length=100),
        ),
    ]
