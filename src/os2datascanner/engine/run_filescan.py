import multiprocessing

from twisted.internet import defer

from .run import StartScan

from .scanners.spiders.filespider import FileSpider
from .scanners.scanner_types.filescanner import FileScanner


class StartFileScan(StartScan, multiprocessing.Process):
    """A scanner application which can be run."""

    def run(self):
        """Updates the scan status and sets the pid.
        Run the scanner, blocking until finished."""
        super().run()

        self.scanner = FileScanner(self.configuration)

        with self.scanner:
            self.start_filescan_crawlers()

    def start_filescan_crawlers(self):
        """Start a file scan."""

        self.logger.info("Beginning crawler process.")

        self.run_crawlers()
        self.crawler_process.start()
        self.logger.info("Crawler process finished.")

    @defer.inlineCallbacks
    def run_crawlers(self):
        self.make_scanner_crawler(FileSpider)
        yield self.crawler_process.crawl(
            self.scanner_crawler, scanner=self.scanner, runner=self)

    def handle_closed(self, spider, reason):
        """Handle the spider being finished."""
        self.filescan_cleanup()
        super().handle_closed(spider, reason)

    def filescan_cleanup(self):
        self.scan_object.webscanner.smb_umount()
