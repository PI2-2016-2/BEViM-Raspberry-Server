# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-23 07:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor_data', '0004_data_job_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='timestamp_ref',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=17),
            preserve_default=False,
        ),
    ]
