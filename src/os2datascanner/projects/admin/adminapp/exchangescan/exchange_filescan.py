"""
Demands:
* starter når den første _done folder er markeret
* hvis filscan indhenter exchange download skal filscan vente indtil en ny folder er markeret med _done.
* Når alt exchange indhold er downloadet skal filscan vide at der ikke er mere indhold at scanne.
"""
import os
import time
import queue
import multiprocessing
import subprocess

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from exchangelib import EWSDate

from .mailscan_exchange import ExchangeServerScan, read_users
from .settings import NUMBER_OF_EMAIL_THREADS
from ..models.scans.scan_model import Scan
from ..models.scannerjobs.scanner_model import Scanner


class ExchangeFilescanner(multiprocessing.Process):
    def __init__(self, scan_id):
        multiprocessing.Process.__init__(self)
        print('Program started')
        self.scan_id = scan_id

        scan_object = Scan.objects.get(pk=self.scan_id)
        valid_domains = scan_object.domains.filter(
            validation_status=Scanner.VALID)
        """Making scan dir if it does not exists"""
        if not os.path.exists(scan_object.scan_dir):
            print('Creating scan dir {}'.format(scan_object.scan_dir))
            os.makedirs(scan_object.scan_dir)

        scan_dir = scan_object.scan_dir + '/'
        """Handling last scannings date"""
        last_scannings_date = None
        if scan_object.do_last_modified_check:
            last_scannings_date = scan_object.exchangescan.last_scannings_date
            if last_scannings_date:
                last_scannings_date = EWSDate.from_date(last_scannings_date)
        """Foreach domain x number of mail processors are started."""
        for domain in valid_domains:
            credentials = (domain.authentication.username,
                           domain.authentication.get_password())
            self.user_queue = multiprocessing.Queue()
            read_users(self.user_queue,
                       domain.exchangedomain.get_userlist_file_path())
            self.done_queue = multiprocessing.Queue()
            mail_ending = domain.url

            scanners = {}
            for i in range(0, NUMBER_OF_EMAIL_THREADS):
                scanners[i] = ExchangeServerScan(
                    credentials,
                    self.user_queue,
                    self.done_queue,
                    scan_dir,
                    mail_ending,
                    start_date=last_scannings_date)
                scanners[i].start()
                print('Started scanner {}'.format(i))
                time.sleep(1)

            self.scanners = scanners
            print('Scanners started...')

    def run(self):
        """
        Starts an exchange mail server scan.
        """
        """
        As long as mail scanners are running file scanners will be started 
        when there is something in the shared queue.
        """
        for key, value in self.scanners.items():
            self.start_folder_scan(self.done_queue)

            while value.is_alive():
                print('Process with pid {} is still alive'.format(value.pid))
                self.start_folder_scan(self.done_queue)
                time.sleep(1)

        self.mark_scan_job_as_done(True)

    def start_folder_scan(self, q):
        """
        Getting next queue item and starting file scan on item, until queue is empty.
        :param q: shared queue
        """
        item = q.get()
        while item is not None:
            print('Getting item from q: {}'.format(item))
            try:
                self.start_filescan(item)
                item = q.get(True, 1)

            except queue.Empty:
                print('Queue is empty')
                item = None

    def start_filescan(self, path):
        """
        Starts a file scan on downloaded exchange folder
        :param path: path to folder
        """
        scan_object = self.update_scan_job_path(path)
        print('Starting file scan for path {}'.format(path))
        scanner_dir = os.path.join(settings.PROJECT_DIR, "scrapy-webscanner")
        log_file = open(scan_object.scan_log_file, "a")
        try:
            process = subprocess.Popen(
                [os.path.join(scanner_dir, 'run.sh'),
                 str(self.scan_id)],
                cwd=scanner_dir,
                stderr=log_file,
                stdout=log_file)
            process.communicate()
        except Exception as e:
            print(e)

    def update_scan_job_path(self, path):
        """
        When an exchange users data has been downloaded
        the path to the downloaded files are stored.
        :param path: path to downloaded files
        :return: scan_object with updated folder_to_scan path
        """
        try:
            scan_object = self.get_scan_object()
            scan_object.folder_to_scan = str(path)
            scan_object.save()
        except Exception as ex:
            print('Error occured while storing path to scan: {}'.format(path))
            print(ex)
        return scan_object

    def get_scan_object(self):
        """Gets the scan object from db"""
        try:
            scan_object = Scan.objects.get_subclass(pk=self.scan_id)
        except ObjectDoesNotExist:
            print('Scan object with id {} does not exists.'.format(
                self.scan_id))
        return scan_object

    def mark_scan_job_as_done(self, is_done):
        """
        Marks the exchange scan job as done
        :param is_done: boolean value marking the job as completed or not.
        :return: the updated scan_object.
        """
        try:
            scan_object = self.get_scan_object()
            scan_object.mark_scan_as_done = is_done
            scan_object.save()
        except Exception as ex:
            print(
                'Error occured while storing path to scan: {}'.format(is_done))
            print(ex)
        return scan_object


# TODO: læg user elementer i en python list og tjek tilsidst eller løbende at alle users er scannet.
