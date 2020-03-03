# Generated by Django 2.2.10 on 2020-02-19 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0005_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultRole',
            fields=[
                ('role_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner_report.Role')),
            ],
            bases=('os2datascanner_report.role',),
        ),
    ]