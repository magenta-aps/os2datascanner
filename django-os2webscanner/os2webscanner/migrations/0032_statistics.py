# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-13 08:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os2webscanner', '0031_auto_20180613_1043'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('files_processed_count', models.IntegerField(default=0)),
                ('files_added_to_the_queue_count', models.IntegerField(default=0)),
                ('files_skipped_count', models.IntegerField(default=0)),
                ('files_failed_count', models.IntegerField(default=0)),
                ('scan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scanjob', to='os2webscanner.Scan', verbose_name='scanjob')),
            ],
        ),
    ]
