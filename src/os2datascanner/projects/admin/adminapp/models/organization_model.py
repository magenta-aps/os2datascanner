from django.db import models
from django.conf import settings


class Organization(models.Model):
    """Represents the organization for each user and scanner, etc.

    Users can only see material related to their own organization.
    """

    name = models.CharField(max_length=256, unique=True, verbose_name='Navn')
    contact_email = models.CharField(max_length=256, verbose_name='Email')
    contact_phone = models.CharField(max_length=256, verbose_name='Telefon')
    do_use_groups = models.BooleanField(
        default=False, editable=settings.DO_USE_GROUPS)
    do_notify_all_scans = models.BooleanField(default=True)

    def __str__(self):
        """Return the name of the organization."""
        return self.name
