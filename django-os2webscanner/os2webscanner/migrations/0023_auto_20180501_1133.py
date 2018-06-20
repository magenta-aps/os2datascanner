# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-01 09:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os2webscanner', '0022_auto_20180501_1119'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048, verbose_name='Url')),
                ('validation_status', models.IntegerField(choices=[(0, 'Ugyldig'), (1, 'Gyldig')], default=0, verbose_name='Valideringsstatus')),
                ('exclusion_rules', models.TextField(blank=True, default='', verbose_name='Ekskluderingsregler')),
                ('authentication', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_domain_authentication', to='os2webscanner.Authentication', verbose_name='Bruger navn')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_domain_groups', to='os2webscanner.Group', verbose_name='Gruppe')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_domain_organization', to='os2webscanner.Organization', verbose_name='Organisation')),
            ],
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='authentication',
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='exclusion_rules',
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='group',
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='id',
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='url',
        ),
        migrations.RemoveField(
            model_name='filedomain',
            name='validation_status',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='authentication',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='exclusion_rules',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='group',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='id',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='url',
        ),
        migrations.RemoveField(
            model_name='webdomain',
            name='validation_status',
        ),
        migrations.AddField(
            model_name='filedomain',
            name='domain_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2webscanner.Domain'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='webdomain',
            name='domain_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2webscanner.Domain'),
            preserve_default=False,
        ),
    ]
