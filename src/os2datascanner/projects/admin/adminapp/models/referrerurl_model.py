from urllib.request import urlopen

from .version_model import Version


class ReferrerUrl(Version):

    """A representation of a referrer URL."""

    class Meta:
        verbose_name = 'Referer URL'

    def __str__(self):
        """Return the URL."""
        return self.url

    @property
    def content(self):
        """Return the content of the target url"""
        try:
            file = urlopen(self.url)
            return file.read()
        except Exception as e:
            return str(e)

    @property
    def broken_urls(self):
        result = self.os2datascanner_webversion_linked_urls.exclude(
            status_code__isnull=True
        ).order_by('url')

        return result
        # .filter(status=None)
        # WebVersion.objects.filter(referrerurls__contains=self, status=None)
