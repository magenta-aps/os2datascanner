# Generated by Django 2.2.10 on 2020-10-02 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0036_copy_rule_relations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scanner',
            name='rules',
        ),
    ]
