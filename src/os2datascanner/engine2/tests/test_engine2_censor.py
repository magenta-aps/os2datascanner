import unittest

from os2datascanner.engine2.model.ews import (
        EWSMailHandle, EWSAccountSource, OFFICE_365_ENDPOINT as CLOUD)
from os2datascanner.engine2.model.smb import SMBSource, SMBHandle
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.derived.zip import ZipSource, ZipHandle
from os2datascanner.engine2.model.derived.filtered import (
        GzipSource, FilteredHandle)


class CensorTests(unittest.TestCase):
    def test_smb_censoring(self):
        example_handles = [
            SMBHandle(
                    SMBSource(
                            "//SERVER/Resource", "username"),
                    "~ocument.docx"),
            SMBCHandle(
                    SMBCSource(
                            "//SERVER/Resource",
                            "username", "topsecret", "WORKGROUP8"),
                    "~ocument.docx"),
        ]

        for handle in example_handles:
            with self.subTest(handle):
                handle = handle.censor()

                self.assertIsNone(handle.source._domain)
                self.assertIsNone(handle.source._password)
                self.assertIsNone(handle.source._user)

    def test_ews_censoring(self):
        example_handles = [
            EWSMailHandle(
                    EWSAccountSource(
                            "internet.invalid",
                            "mail.internet.invalid",
                            "administrator", "h4ckme",
                            "secretary"),
                    "notavalidfolderid.notavalidmailid",
                    "Re: Re: Re: You may already have won! (was Fwd: Spam)",
                    "Inbox", "notavalidentryid")
        ]

        for handle in example_handles:
            with self.subTest(handle):
                censored_handle = handle.censor()

                self.assertIsNone(censored_handle.source._admin_user)
                self.assertIsNone(censored_handle.source._admin_password)
                self.assertEqual(
                        handle._mail_subject,
                        censored_handle._mail_subject,
                        "subject not preserved")
                self.assertEqual(
                        handle._folder_name,
                        censored_handle._folder_name,
                        "folder name not preserved")
                self.assertEqual(
                        handle._entry_id,
                        censored_handle._entry_id,
                        "entry_id not preserved")

    def test_nested_censoring(self):
        example_handles = [
            ZipHandle(
                    ZipSource(
                            SMBCHandle(
                                    SMBCSource(
                                            "//SERVER/Resource",
                                            "username", driveletter="W"),
                                    "Confidential Documents.zip")),
                    "doc/Personal Information.docx"),
            FilteredHandle(
                    GzipSource(
                            SMBHandle(
                                    SMBSource(
                                            "//SERVER/usr", "username"),
                                    "share/doc/coreutils"
                                    "/changelog.Debian.gz")),
                    "changelog.Debian"),
        ]

        for handle in example_handles:
            with self.subTest(handle):
                self.assertIsNotNone(handle.source.handle.source._user)
                handle = handle.censor()
                self.assertIsNone(handle.source.handle.source._user)
