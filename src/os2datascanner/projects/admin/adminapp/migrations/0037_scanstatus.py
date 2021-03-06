# Generated by Django 2.2.10 on 2020-11-25 14:21

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0036_sbsysscanner'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScanStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scan_tag', django.contrib.postgres.fields.jsonb.JSONField(unique=True, verbose_name='Scan tag')),
                ('total_sources', models.IntegerField(null=True, verbose_name='Antal kilder')),
                ('explored_sources', models.IntegerField(null=True, verbose_name='Udforskede kilder')),
                ('total_objects', models.IntegerField(null=True, verbose_name='Antal objekter')),
                ('scanned_objects', models.IntegerField(null=True, verbose_name='Scannede objekter')),
                ('scanned_size', models.BigIntegerField(null=True, verbose_name='Størrelse af scannede objekter')),
                ('scanner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='os2datascanner.Scanner', verbose_name='Tilknyttet scannerjob')),
            ],
            options={
                'verbose_name_plural': 'scan statuses',
            },
        ),
    ]
