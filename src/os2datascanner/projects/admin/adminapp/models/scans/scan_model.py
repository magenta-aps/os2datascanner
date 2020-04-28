# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

import datetime
import os
import shutil

import dateutil.tz
import structlog
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.db import models, transaction
from django.db.models.aggregates import Count
from django.utils import timezone
from django.utils.functional import cached_property
from model_utils.fields import MonitorField, StatusField

from ..match_model import Match
from ..rules.rule_model import Rule
from ..scannerjobs.scanner_model import Scanner
from ..sensitivity_level import Sensitivity
from ..userprofile_model import UserProfile

timezone.activate(timezone.get_default_timezone())

logger = structlog.get_logger()


class Scan(models.Model):

    """An actual instance of the scanning process done by a scanner."""

    def __init__(self, *args, **kwargs):
        """Initialize a new scan.
        Stores the old status of the scan for later use.
        """
        super().__init__(*args, **kwargs)
        self._old_status = self.status

    @property
    def logger(self):
        return logger.bind(scan_id=self.pk, scan_status=self.status)

    @property
    def matches(self):
        return Match.objects.filter(url__scan=self)

    @property
    def urls(self):
        return self.versions.values('location')

    # Begin setup copied from scanner
    scanner = models.ForeignKey(Scanner,
                                null=True, verbose_name='webscanner',
                                related_name='webscans',
                                on_delete=models.SET_NULL)

    is_visible = models.BooleanField(default=True)

    do_ocr = models.BooleanField(default=False, verbose_name='Scan billeder')


    do_last_modified_check = models.BooleanField(
        default=True,
        verbose_name='Tjek dato for sidste ændring',
        help_text='Scan udelukkende filer der rapporteres som nyere end '
                  'sidste scanning',
    )

    columns = models.CharField(validators=[validate_comma_separated_integer_list],
                               max_length=128,
                               null=True,
                               blank=True
                               )

    rules = models.ManyToManyField(Rule,
                                   blank=True,
                                   verbose_name='Regler',
                                   related_name='scans')
    recipients = models.ManyToManyField(UserProfile, blank=True)

    # Spreadsheet annotation and replacement parameters

    # Save a copy of any spreadsheets scanned with annotations
    # in each row where matches were found. If this is enabled and any of
    # the replacement parameters are enabled (e.g. do_cpr_replace), matches
    # will also be replaced with the specified text (e.g. cpr_replace_text).
    output_spreadsheet_file = models.BooleanField(default=False)

    # Replace CPRs?
    do_cpr_replace = models.BooleanField(default=False)
    # Text to replace CPRs with
    cpr_replace_text = models.CharField(max_length=2048, null=True,
                                        blank=True)
    # Replace names?
    do_name_replace = models.BooleanField(default=False)
    # Text to replace names with
    name_replace_text = models.CharField(max_length=2048, null=True,
                                         blank=True)
    # Replace addresses?
    do_address_replace = models.BooleanField(default=False)
    # Text to replace addresses with
    address_replace_text = models.CharField(max_length=2048, null=True,
                                            blank=True)

    # Scan status
    NEW = "NEW"
    STARTED = "STARTED"
    DONE = "DONE"
    FAILED = "FAILED"

    STATUS = (
        (NEW, "Ny"),
        (STARTED, "I gang"),
        (DONE, "Færdig"),
        (FAILED, "Mislykket"),
    )

    status = StatusField(max_length=max(map(len, dict(STATUS).values())))

    creation_time = MonitorField(
        monitor='status',
        when=[NEW],
        default=timezone.now,
        null=False,
        verbose_name='Oprettelsestidspunkt',
    )
    start_time = MonitorField(
        monitor='status',
        when=[STARTED],
        null=True,
        default=None,
        verbose_name='Starttidspunkt',
    )
    end_time = MonitorField(
        monitor='status',
        when=[DONE, FAILED],
        null=True,
        default=None,
        verbose_name='Sluttidspunkt',
    )

    pause_non_ocr_conversions = models.BooleanField(default=False,
                                                    verbose_name='Pause ' +
                                                                 'non-OCR conversions')

    @cached_property
    def webscanner(self):
        return Scanner.objects.get_subclass(pk=self.scanner_id)

    @property
    def status_text(self):
        """A display text for the scan's status.

        Relies on the restriction that the status must be one of the allowed
        values.
        """
        text = [t for s, t in Scan.STATUS if self.status == s][0]
        return text

    @property
    def scan_dir(self):
        """The directory associated with this scan."""
        return os.path.join(settings.VAR_DIR, 'scan_%s' % self.pk)

    @property
    def scan_log_dir(self):
        """Return the path to the scan log dir."""
        log_dir = os.path.join(settings.VAR_DIR, 'logs', 'scans')
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        return log_dir

    @property
    def scan_log_file(self):
        """Return the log file path associated with this scan."""
        return os.path.join(self.scan_log_dir, 'scan_%s.log' % self.pk)

    @property
    def scan_output_files_dir(self):
        """Return the path to the scan output files dir."""
        return os.path.join(settings.VAR_DIR, 'output_files')

    @property
    def scan_output_file(self):
        """Return the output file path associated with this scan.

        Note that this currently only supports one output file per scan.
        """
        return os.path.join(self.scan_output_files_dir,
                            'scan_%s.csv' % self.pk)

    # Occurrence log - mainly for the scanner to notify when something FAILS.
    def log_occurrence(self, string):
        self.logger.debug('scan_occurrence', occurrence=string)

        with open(self.occurrence_log_file, "a") as f:
            f.write("{0}\n".format(string))

    @property
    def occurrence_log(self):
        try:
            with open(self.occurrence_log_file, "r") as f:
                return f.read()
        except IOError:
            return ""

    @property
    def occurrence_log_file(self):
        """Return the file path to this scan's occurrence log."""
        return os.path.join(self.scan_log_dir, 'occurrence_%s.log' % self.pk)

    # Reason for failure
    reason = models.CharField(max_length=1024, blank=True, default="",
                              verbose_name='Årsag')
    pid = models.IntegerField(null=True, blank=True, verbose_name='Pid')

    @property
    def no_of_matches(self):
        """Return the number of matches for this scan."""
        return self.matches.count()

    @property
    def no_of_critical_matches(self):
        """Return the number of *critical* matches, <= no_of_matches."""
        return self.matches.filter(sensitivity=Sensitivity.HIGH).count()

    def __str__(self):
        """Return the name of the scan's scanner combined with a timestamp."""
        if self.creation_time:
            ts = (
                self.creation_time
                .astimezone(dateutil.tz.tzlocal())
                .replace(microsecond=0, tzinfo=None)
            )
            return "{} — {}".format(self.scanner, ts)
        else:
            return str(self.scanner)

    def save(self, *args, **kwargs):
        """Save changes to the scan.

        Sets the end_time for the scan, notifies the associated user by email,
        deletes any remaining queue items and deletes the temporary directory
        used by the scan.
        """
        # Actual save
        super().save(*args, **kwargs)
        # Post-save stuff

        if self.status in [Scan.DONE, Scan.FAILED] and \
                (self._old_status != self.status):
            # Send email
            from ...utils import notify_user
            try:
                notify_user(self)
            except IOError:
                self.log_occurrence("Unable to send email notification!")

            self.cleanup_finished_scan()
            self._old_status = self.status

    def cleanup_finished_scan(self):
        """Delete pending conversion queue items and remove the scan dir."""
        # remove all files associated with the scan
        if self.is_scan_dir_writable():
            self.delete_scan_dir()

    @classmethod
    def cleanup_finished_scans(cls, oldest_end_time: datetime.datetime):
        """Cleanup convqueue items from finished scans.

        Only Scans that have ended since oldest_end_time are considered.
        """

        inactive_scans = cls.objects.filter(
            models.Q(status__in=(Scan.DONE, Scan.FAILED)),
            (
                models.Q(end_time__gt=oldest_end_time) |
                models.Q(end_time__isnull=True)
            ),
        )

        logger.debug(
            "cleanup_finished_scans",
            since=oldest_end_time.isoformat(),
            scans=len(inactive_scans),
            type=cls.__name__,
        )

        for scan in inactive_scans:
            scan.cleanup_finished_scan()

    @classmethod
    def check_running_scans(cls):
        with transaction.atomic():
            running_scans = cls.objects.filter(
                status=cls.STARTED
            ).select_for_update(nowait=True)

            logger.debug(
                "check_running_scans",
                scans=len(running_scans),
                type=cls.__name__,
            )

            for scan in running_scans:
                if not scan.pid and not hasattr(scan, "exchangescan"):
                    continue
                try:
                    # Check if process is still running
                    os.kill(scan.pid, 0)
                    logger.debug(
                        "scan_ok", scan=scan.pk, scan_pid=scan.pid
                    )
                except OSError:
                    logger.critical(
                        "scan_disappeared",
                        scan_id=scan.pk,
                        scan_pid=scan.pid,
                        exc_info=True,
                    )

                    scan.set_scan_status_failed(
                        "FAILED: process {} disappeared".format(scan.pid)
                    )

    def delete_scan_dir(self):
        shutil.rmtree(self.scan_dir, True)
        self.logger.debug(
            "scan_dir_deleted",
            scan_id=self.pk,
            dir=self.scan_dir,
        )

    def is_scan_dir_writable(self):
        """Return whether the scan's directory exists and is writable."""
        return os.access(self.scan_dir, os.W_OK)

    def get_absolute_url(self):
        """Get the URL for this report - used to format URLs."""
        from django.core.urlresolvers import reverse
        return reverse('report', args=[str(self.id)])

    def set_scan_status_start(self):
        # Update start_time to now and status to STARTED
        self.status = Scan.STARTED
        self.reason = ""
        self.logger.debug('scan_started')
        self.pid = os.getpid()
        self.save()

    def set_scan_status_done(self):
        self.status = Scan.DONE
        self.pid = None
        self.reason = ""
        self.save()

    def set_scan_status_failed(self, reason):
        self.pid = None
        self.status = Scan.FAILED
        if reason is None:
            self.reason = "Killed"
        else:
            self.reason = reason

        self.log_occurrence(self.reason)
        self.save()

    # Create method - copies fields from scanner
    def create(self, scanner):
        """ Create and copy fields from scanner. """
        self.is_visible = scanner.is_visible
        self.do_ocr = scanner.do_ocr
        self.do_last_modified_check = scanner.do_last_modified_check
        self.columns = scanner.columns
        self.output_spreadsheet_file = scanner.output_spreadsheet_file
        self.do_cpr_replace = scanner.do_cpr_replace
        self.cpr_replace_text = scanner.cpr_replace_text
        self.do_name_replace = scanner.do_name_replace
        self.name_replace_text = scanner.name_replace_text
        self.do_address_replace = scanner.do_address_replace
        self.address_replace_text = scanner.address_replace_text
        self.set_status_new(scanner)

        return self

    def set_status_new(self, scanner):
        self.status = Scan.NEW
        self.scanner = scanner
        self.save()
        self.rules.add(*scanner.rules.all())
        self.recipients.add(*scanner.recipients.all())

    class Meta:
        abstract = False

        verbose_name = 'Report'
        ordering = ['-creation_time']
