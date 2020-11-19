from django.db import models
from django.conf import settings
import uuid

class Organization(models.Model):

    """Represents the organization for each user and scanner, etc.

    Users can only see material related to their own organization.
    """

    name = models.CharField(max_length=256, unique=True, verbose_name='Navn', 
                            editable=False)
    contact_email = models.CharField(max_length=256, verbose_name='Email',
                            editable=False)
    contact_phone = models.CharField(max_length=256, verbose_name='Telefon',
                            editable=False)
    do_use_groups = models.BooleanField(default=False, editable=False)
    do_notify_all_scans = models.BooleanField(default=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        """Return the name of the organization."""
        return self.name

    def to_json_object(self):
        return {
            "name": self.name,
            "uuid": str(self.uuid),
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "do_use_groups": self.do_use_groups,
            "do_notify_all_scans": self.do_notify_all_scans,
        }
