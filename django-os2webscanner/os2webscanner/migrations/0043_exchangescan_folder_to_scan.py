# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-26 13:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2webscanner', '0042_merge_20180717_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangescan',
            name='folder_to_scan',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
    ]
