"""Unit-test util for tests os2webscanner.tests"""
# flake8: noqa pydocstyle:noqa
from os2datascanner.projects.admin.adminapp.models.organization_model import Organization
from os2datascanner.projects.admin.adminapp.models.scans.scan_model import Scan


class CreateOrganization(object):

    def create_organization(self):
        return Organization.objects.create(
            name='Magenta',
            contact_email='info@magenta.dk',
            contact_phone='39393939'
        )


class CreateScan(object):

    def create_filescan(self):
        return Scan.objects.create(
            status=Scan.DONE
        )
