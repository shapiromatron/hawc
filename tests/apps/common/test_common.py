from django.core.exceptions import ValidationError
from django.test import TestCase

from hawc.apps.common import validators


class CustomURLValidtor(TestCase):
    def test_urls(self):
        # ensure that standard URL cases work as expected
        validator = validators.CustomURLValidator()
        for url in [
            "http://www.example.com",
            "http://example.com",
            "http://www.example.com/abc/def/efg?x=1&y=2",
        ]:
            assert validator(url) is None

        for url in [
            "random://example.com",
            "www.example.com",
            "http://example",
            "http://example/foo/bar?x=1&y=2",
        ]:
            with self.assertRaises(ValidationError):
                validator(url)

    def test_smbs(self):
        # ensure that SMB work as expected
        validator = validators.CustomURLValidator()
        for path in [
            "smb://path/to/stuff/",
            "smb://path/to/stuff.pdf",
            "smb://path/to/stuff%20with%20spaces.txt",
        ]:
            assert validator(path) is None

        for path in [
            "smb://path/to/stuff with spaces.txt",
        ]:
            with self.assertRaises(ValidationError):
                validator(path)
