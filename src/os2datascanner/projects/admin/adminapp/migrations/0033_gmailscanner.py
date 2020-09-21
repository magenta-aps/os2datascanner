# Generated by Django 2.2.10 on 2020-09-21 13:28

from django.db import migrations, models
import django.db.models.deletion
import os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail_model


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0032_msgraphfilescanner'),
    ]

    operations = [
        migrations.CreateModel(
            name='GmailScanner',
            fields=[
                ('scanner_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='os2datascanner.Scanner')),
                ('service_account_file_gmail', models.FileField(upload_to='gmail/serviceaccount/', validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail_model.GmailScanner.validate_filetype_json])),
                ('user_emails_gmail', models.FileField(upload_to='gmail/users/', validators=[os2datascanner.projects.admin.adminapp.models.scannerjobs.gmail_model.GmailScanner.validate_filetype_csv])),
            ],
            bases=('os2datascanner.scanner',),
        ),
    ]
