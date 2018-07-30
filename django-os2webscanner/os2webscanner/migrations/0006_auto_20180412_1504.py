# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-04-12 13:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('os2webscanner', '0005_auto_20180411_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='Authentication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, default='', max_length=1024, verbose_name='Bruger navn')),
                ('iv', models.BinaryField(blank=True, max_length=32, verbose_name='InitialiseringsVektor')),
                ('ciphertext', models.BinaryField(blank=True, max_length=1024, verbose_name='Password')),
            ],
        ),
        migrations.CreateModel(
            name='AuthenticationMethods',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('methodname', models.CharField(max_length=1024, unique=True, verbose_name='Login method')),
            ],
        ),
        migrations.CreateModel(
            name='FileConversionQueueItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(max_length=4096, verbose_name='Fil')),
                ('type', models.CharField(max_length=256, verbose_name='Type')),
                ('page_no', models.IntegerField(null=True, verbose_name='Side')),
                ('status', models.CharField(choices=[('NEW', 'Ny'), ('PROCESSING', 'I gang'), ('FAILED', 'Fejlet')], default='NEW', max_length=10, verbose_name='Status')),
                ('process_id', models.IntegerField(blank=True, null=True, verbose_name='Proces id')),
                ('process_start_time', models.DateTimeField(blank=True, null=True, verbose_name='Proces starttidspunkt')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048, verbose_name='Url')),
                ('validation_status', models.IntegerField(choices=[(0, 'Ugyldig'), (1, 'Gyldig')], default=0, verbose_name='Valideringsstatus')),
                ('exclusion_rules', models.TextField(blank=True, default='', verbose_name='Ekskluderingsregler')),
                ('authentication', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_filedomain_authentication', to='os2webscanner.Authentication', verbose_name='Bruger navn')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_filedomain_groups', to='os2webscanner.Group', verbose_name='Gruppe')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_filedomain_organization', to='os2webscanner.Organization', verbose_name='Organisation')),
            ],
            options={
                'db_table': 'os2webscanner_filedomain',
            },
        ),
        migrations.CreateModel(
            name='FileMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matched_data', models.CharField(max_length=1024, verbose_name='Data match')),
                ('matched_rule', models.CharField(max_length=256, verbose_name='Regel match')),
                ('sensitivity', models.IntegerField(choices=[(0, 'Grøn'), (1, 'Gul'), (2, 'Rød')], default=2, verbose_name='Følsomhed')),
                ('match_context', models.CharField(max_length=1152, verbose_name='Kontekst')),
                ('page_no', models.IntegerField(null=True, verbose_name='Side')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileScan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Starttidspunkt')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='Sluttidspunkt')),
                ('is_visible', models.BooleanField(default=True)),
                ('whitelisted_names', models.TextField(blank=True, default='', max_length=4096, verbose_name='Godkendte navne')),
                ('blacklisted_names', models.TextField(blank=True, default='', max_length=4096, verbose_name='Sortlistede navne')),
                ('whitelisted_addresses', models.TextField(blank=True, default='', max_length=4096, verbose_name='Godkendte adresser')),
                ('blacklisted_addresses', models.TextField(blank=True, default='', max_length=4096, verbose_name='Sortlistede adresser')),
                ('whitelisted_cprs', models.TextField(blank=True, default='', max_length=4096, verbose_name='Godkendte CPR-numre')),
                ('do_cpr_scan', models.BooleanField(default=True, verbose_name='CPR')),
                ('do_name_scan', models.BooleanField(default=False, verbose_name='Navn')),
                ('do_address_scan', models.BooleanField(default=False, verbose_name='Adresse')),
                ('do_ocr', models.BooleanField(default=False, verbose_name='Scan billeder')),
                ('do_cpr_modulus11', models.BooleanField(default=True, verbose_name='Tjek modulus-11')),
                ('do_cpr_ignore_irrelevant', models.BooleanField(default=True, verbose_name='Ignorer ugyldige fødselsdatoer')),
                ('do_last_modified_check', models.BooleanField(default=True, verbose_name='Tjek sidst ændret dato')),
                ('columns', models.CommaSeparatedIntegerField(blank=True, max_length=128, null=True)),
                ('output_spreadsheet_file', models.BooleanField(default=False)),
                ('do_cpr_replace', models.BooleanField(default=False)),
                ('cpr_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_name_replace', models.BooleanField(default=False)),
                ('name_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_address_replace', models.BooleanField(default=False)),
                ('address_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('status', models.CharField(choices=[('NEW', 'Ny'), ('STARTED', 'I gang'), ('DONE', 'OK'), ('FAILED', 'Fejlet')], default='NEW', max_length=10)),
                ('pause_non_ocr_conversions', models.BooleanField(default=False, verbose_name='Pause non-OCR conversions')),
                ('reason', models.CharField(blank=True, default='', max_length=1024, verbose_name='Årsag')),
                ('pid', models.IntegerField(blank=True, null=True, verbose_name='Pid')),
                ('domains', models.ManyToManyField(to='os2webscanner.FileDomain', verbose_name='Domæner')),
                ('recipients', models.ManyToManyField(blank=True, to='os2webscanner.UserProfile')),
                ('regex_rules', models.ManyToManyField(blank=True, to='os2webscanner.RegexRule', verbose_name='Regex regler')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileScanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Navn')),
                ('username', models.CharField(blank=True, default='', max_length=1024, verbose_name='Bruger navn')),
                ('iv', models.BinaryField(blank=True, max_length=32, verbose_name='InitialiseringsVektor')),
                ('ciphertext', models.BinaryField(blank=True, max_length=1024, verbose_name='Password')),
                ('schedule', recurrence.fields.RecurrenceField(max_length=1024, verbose_name='Planlagt afvikling')),
                ('do_cpr_scan', models.BooleanField(default=True, verbose_name='CPR')),
                ('do_name_scan', models.BooleanField(default=False, verbose_name='Navn')),
                ('do_address_scan', models.BooleanField(default=False, verbose_name='Adresse')),
                ('do_ocr', models.BooleanField(default=False, verbose_name='Scan billeder')),
                ('do_last_modified_check', models.BooleanField(default=True, verbose_name='Tjek sidst ændret dato')),
                ('do_cpr_modulus11', models.BooleanField(default=True, verbose_name='Tjek modulus-11')),
                ('do_cpr_ignore_irrelevant', models.BooleanField(default=True, verbose_name='Ignorer ugyldige fødselsdatoer')),
                ('columns', models.CommaSeparatedIntegerField(blank=True, max_length=128, null=True)),
                ('output_spreadsheet_file', models.BooleanField(default=False)),
                ('do_cpr_replace', models.BooleanField(default=False)),
                ('cpr_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_name_replace', models.BooleanField(default=False)),
                ('name_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_address_replace', models.BooleanField(default=False)),
                ('address_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('encoded_process_urls', models.CharField(blank=True, max_length=262144, null=True)),
                ('do_run_synchronously', models.BooleanField(default=False)),
                ('is_visible', models.BooleanField(default=True)),
                ('domains', models.ManyToManyField(related_name='filedomains', to='os2webscanner.FileDomain', verbose_name='Fil Domæner')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.Group', verbose_name='Gruppe')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.Organization', verbose_name='Organisation')),
                ('recipients', models.ManyToManyField(blank=True, to='os2webscanner.UserProfile', verbose_name='Modtagere')),
                ('regex_rules', models.ManyToManyField(blank=True, to='os2webscanner.RegexRule', verbose_name='Regex regler')),
            ],
            options={
                'db_table': 'os2webscanner_filescanner',
            },
        ),
        migrations.CreateModel(
            name='FileUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048, verbose_name='Url')),
                ('mime_type', models.CharField(max_length=256, verbose_name='Mime-type')),
                ('status_code', models.IntegerField(blank=True, null=True, verbose_name='Status code')),
                ('status_message', models.CharField(blank=True, max_length=256, null=True, verbose_name='Status Message')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048, verbose_name='Url')),
                ('validation_status', models.IntegerField(choices=[(0, 'Ugyldig'), (1, 'Gyldig')], default=0, verbose_name='Valideringsstatus')),
                ('exclusion_rules', models.TextField(blank=True, default='', verbose_name='Ekskluderingsregler')),
                ('validation_method', models.IntegerField(choices=[(0, 'robots.txt'), (1, 'webscan.html'), (2, 'Meta-felt')], default=0, verbose_name='Valideringsmetode')),
                ('sitemap', models.FileField(blank=True, upload_to='sitemaps', verbose_name='Sitemap Fil')),
                ('sitemap_url', models.CharField(blank=True, default='', max_length=2048, verbose_name='Sitemap Url')),
                ('download_sitemap', models.BooleanField(default=True, verbose_name='Hent Sitemap fra serveren')),
                ('authentication', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_webdomain_authentication', to='os2webscanner.Authentication', verbose_name='Bruger navn')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_webdomain_groups', to='os2webscanner.Group', verbose_name='Gruppe')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_webdomain_organization', to='os2webscanner.Organization', verbose_name='Organisation')),
            ],
            options={
                'db_table': 'os2webscanner_webdomain',
            },
        ),
        migrations.CreateModel(
            name='WebMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matched_data', models.CharField(max_length=1024, verbose_name='Data match')),
                ('matched_rule', models.CharField(max_length=256, verbose_name='Regel match')),
                ('sensitivity', models.IntegerField(choices=[(0, 'Grøn'), (1, 'Gul'), (2, 'Rød')], default=2, verbose_name='Følsomhed')),
                ('match_context', models.CharField(max_length=1152, verbose_name='Kontekst')),
                ('page_no', models.IntegerField(null=True, verbose_name='Side')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebScan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Starttidspunkt')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='Sluttidspunkt')),
                ('is_visible', models.BooleanField(default=True)),
                ('whitelisted_names', models.TextField(blank=True, default='', max_length=4096, verbose_name='Godkendte navne')),
                ('blacklisted_names', models.TextField(blank=True, default='', max_length=4096, verbose_name='Sortlistede navne')),
                ('whitelisted_addresses', models.TextField(blank=True, default='', max_length=4096, verbose_name='Godkendte adresser')),
                ('blacklisted_addresses', models.TextField(blank=True, default='', max_length=4096, verbose_name='Sortlistede adresser')),
                ('whitelisted_cprs', models.TextField(blank=True, default='', max_length=4096, verbose_name='Godkendte CPR-numre')),
                ('do_cpr_scan', models.BooleanField(default=True, verbose_name='CPR')),
                ('do_name_scan', models.BooleanField(default=False, verbose_name='Navn')),
                ('do_address_scan', models.BooleanField(default=False, verbose_name='Adresse')),
                ('do_ocr', models.BooleanField(default=False, verbose_name='Scan billeder')),
                ('do_cpr_modulus11', models.BooleanField(default=True, verbose_name='Tjek modulus-11')),
                ('do_cpr_ignore_irrelevant', models.BooleanField(default=True, verbose_name='Ignorer ugyldige fødselsdatoer')),
                ('do_last_modified_check', models.BooleanField(default=True, verbose_name='Tjek sidst ændret dato')),
                ('columns', models.CommaSeparatedIntegerField(blank=True, max_length=128, null=True)),
                ('output_spreadsheet_file', models.BooleanField(default=False)),
                ('do_cpr_replace', models.BooleanField(default=False)),
                ('cpr_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_name_replace', models.BooleanField(default=False)),
                ('name_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_address_replace', models.BooleanField(default=False)),
                ('address_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('status', models.CharField(choices=[('NEW', 'Ny'), ('STARTED', 'I gang'), ('DONE', 'OK'), ('FAILED', 'Fejlet')], default='NEW', max_length=10)),
                ('pause_non_ocr_conversions', models.BooleanField(default=False, verbose_name='Pause non-OCR conversions')),
                ('reason', models.CharField(blank=True, default='', max_length=1024, verbose_name='Årsag')),
                ('pid', models.IntegerField(blank=True, null=True, verbose_name='Pid')),
                ('do_link_check', models.BooleanField(default=False, verbose_name='Tjek links')),
                ('do_external_link_check', models.BooleanField(default=False, verbose_name='Eksterne links')),
                ('do_last_modified_check_head_request', models.BooleanField(default=True, verbose_name='Brug HTTP HEAD request')),
                ('do_collect_cookies', models.BooleanField(default=False, verbose_name='Saml cookies')),
                ('domains', models.ManyToManyField(to='os2webscanner.WebDomain', verbose_name='Domæner')),
                ('recipients', models.ManyToManyField(blank=True, to='os2webscanner.UserProfile')),
                ('regex_rules', models.ManyToManyField(blank=True, to='os2webscanner.RegexRule', verbose_name='Regex regler')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebScanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Navn')),
                ('username', models.CharField(blank=True, default='', max_length=1024, verbose_name='Bruger navn')),
                ('iv', models.BinaryField(blank=True, max_length=32, verbose_name='InitialiseringsVektor')),
                ('ciphertext', models.BinaryField(blank=True, max_length=1024, verbose_name='Password')),
                ('schedule', recurrence.fields.RecurrenceField(max_length=1024, verbose_name='Planlagt afvikling')),
                ('do_cpr_scan', models.BooleanField(default=True, verbose_name='CPR')),
                ('do_name_scan', models.BooleanField(default=False, verbose_name='Navn')),
                ('do_address_scan', models.BooleanField(default=False, verbose_name='Adresse')),
                ('do_ocr', models.BooleanField(default=False, verbose_name='Scan billeder')),
                ('do_last_modified_check', models.BooleanField(default=True, verbose_name='Tjek sidst ændret dato')),
                ('do_cpr_modulus11', models.BooleanField(default=True, verbose_name='Tjek modulus-11')),
                ('do_cpr_ignore_irrelevant', models.BooleanField(default=True, verbose_name='Ignorer ugyldige fødselsdatoer')),
                ('columns', models.CommaSeparatedIntegerField(blank=True, max_length=128, null=True)),
                ('output_spreadsheet_file', models.BooleanField(default=False)),
                ('do_cpr_replace', models.BooleanField(default=False)),
                ('cpr_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_name_replace', models.BooleanField(default=False)),
                ('name_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('do_address_replace', models.BooleanField(default=False)),
                ('address_replace_text', models.CharField(blank=True, max_length=2048, null=True)),
                ('encoded_process_urls', models.CharField(blank=True, max_length=262144, null=True)),
                ('do_run_synchronously', models.BooleanField(default=False)),
                ('is_visible', models.BooleanField(default=True)),
                ('do_link_check', models.BooleanField(default=False, verbose_name='Tjek links')),
                ('do_external_link_check', models.BooleanField(default=False, verbose_name='Eksterne links')),
                ('do_last_modified_check_head_request', models.BooleanField(default=True, verbose_name='Brug HTTP HEAD request')),
                ('do_collect_cookies', models.BooleanField(default=False, verbose_name='Saml cookies')),
                ('domains', models.ManyToManyField(related_name='webdomains', to='os2webscanner.WebDomain', verbose_name='Web Domæner')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.Group', verbose_name='Gruppe')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.Organization', verbose_name='Organisation')),
                ('recipients', models.ManyToManyField(blank=True, to='os2webscanner.UserProfile', verbose_name='Modtagere')),
                ('regex_rules', models.ManyToManyField(blank=True, to='os2webscanner.RegexRule', verbose_name='Regex regler')),
            ],
            options={
                'db_table': 'os2webscanner_webscanner',
            },
        ),
        migrations.CreateModel(
            name='WebUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048, verbose_name='Url')),
                ('mime_type', models.CharField(max_length=256, verbose_name='Mime-type')),
                ('status_code', models.IntegerField(blank=True, null=True, verbose_name='Status code')),
                ('status_message', models.CharField(blank=True, max_length=256, null=True, verbose_name='Status Message')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameModel(
            old_name='ConversionQueueItem',
            new_name='WebConversionQueueItem',
        ),
        migrations.RemoveField(
            model_name='domain',
            name='group',
        ),
        migrations.RemoveField(
            model_name='domain',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='match',
            name='scan',
        ),
        migrations.RemoveField(
            model_name='match',
            name='url',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='domains',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='recipients',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='regex_rules',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='scanner',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='domains',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='group',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='recipients',
        ),
        migrations.RemoveField(
            model_name='scanner',
            name='regex_rules',
        ),
        migrations.RemoveField(
            model_name='url',
            name='referrers',
        ),
        migrations.RemoveField(
            model_name='url',
            name='scan',
        ),
        migrations.AlterField(
            model_name='referrerurl',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.WebScan', verbose_name='Scan'),
        ),
        migrations.AlterField(
            model_name='summary',
            name='scanners',
            field=models.ManyToManyField(blank=True, to='os2webscanner.WebScanner', verbose_name='Scannere'),
        ),
        migrations.AlterField(
            model_name='urllastmodified',
            name='scanner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.WebScanner', verbose_name='WebScanner'),
        ),
        migrations.AlterField(
            model_name='webconversionqueueitem',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.WebUrl', verbose_name='Url'),
        ),
        migrations.DeleteModel(
            name='Domain',
        ),
        migrations.DeleteModel(
            name='Match',
        ),
        migrations.DeleteModel(
            name='Scan',
        ),
        migrations.DeleteModel(
            name='Scanner',
        ),
        migrations.DeleteModel(
            name='Url',
        ),
        migrations.AddField(
            model_name='weburl',
            name='referrers',
            field=models.ManyToManyField(related_name='os2webscanner_weburl_linked_urls', to='os2webscanner.ReferrerUrl', verbose_name='Referrers'),
        ),
        migrations.AddField(
            model_name='weburl',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='os2webscanner.WebScan', verbose_name='Scan'),
        ),
        migrations.AddField(
            model_name='webscan',
            name='scanner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webscans', to='os2webscanner.WebScanner', verbose_name='webscanner'),
        ),
        migrations.AddField(
            model_name='webmatch',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_webmatch_matches', to='os2webscanner.WebScan', verbose_name='Scan'),
        ),
        migrations.AddField(
            model_name='webmatch',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.WebUrl', verbose_name='Url'),
        ),
        migrations.AddField(
            model_name='fileurl',
            name='referrers',
            field=models.ManyToManyField(related_name='os2webscanner_fileurl_linked_urls', to='os2webscanner.ReferrerUrl', verbose_name='Referrers'),
        ),
        migrations.AddField(
            model_name='fileurl',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='os2webscanner.FileScan', verbose_name='Scan'),
        ),
        migrations.AddField(
            model_name='filescan',
            name='scanner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filescans', to='os2webscanner.FileScanner', verbose_name='filescanner'),
        ),
        migrations.AddField(
            model_name='filematch',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='os2webscanner_filematch_matches', to='os2webscanner.FileScan', verbose_name='Scan'),
        ),
        migrations.AddField(
            model_name='filematch',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.FileUrl', verbose_name='Url'),
        ),
        migrations.AddField(
            model_name='fileconversionqueueitem',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='os2webscanner.FileUrl', verbose_name='Url'),
        ),
    ]