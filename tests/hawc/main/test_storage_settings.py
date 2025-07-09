import importlib
import os
import sys
from unittest.mock import patch

import boto3
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from moto import mock_aws
from storages.backends.s3boto3 import S3StaticStorage


class S3StorageConfigurationTest(TestCase):
    """Test that base.py correctly configures S3 storage based on environment variables."""

    def setUp(self):
        """Store original modules for cleanup."""
        self.original_modules = sys.modules.copy()
        self.original_environ = os.environ.copy()

    def tearDown(self):
        """Restore original modules and environment."""
        os.environ.clear()
        os.environ.update(self.original_environ)

        modules_to_remove = [
            key
            for key in sys.modules.keys()
            if key not in self.original_modules and key.startswith("hawc.main.settings")
        ]
        for module in modules_to_remove:
            del sys.modules[module]

    def reload_settings_module(self):
        """Reload the settings module to pick up environment changes."""
        modules_to_clear = [
            "hawc.main.settings.base",
            "hawc.main.settings",
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

        import hawc.main.settings.base

        importlib.reload(hawc.main.settings.base)
        return hawc.main.settings.base

    @patch.dict(
        os.environ,
        {
            "HAWC_USE_S3_STORAGE": "true",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_STORAGE_BUCKET_NAME": "test-bucket",
            "AWS_DEFAULT_ACL": "public-read",
            "AWS_S3_REGION_NAME": "us-west-2",
            "AWS_S3_FILE_OVERWRITE": "True",
        },
    )
    def test_s3_storage_configuration_from_env(self):
        """Test that S3 storage is properly configured from environment variables."""
        base_settings = self.reload_settings_module()

        self.assertTrue(base_settings.USE_S3_STORAGE)

        self.assertIn("default", base_settings.STORAGES)
        self.assertIn("private", base_settings.STORAGES)
        self.assertIn("staticfiles", base_settings.STORAGES)

        default_storage_config = base_settings.STORAGES["default"]
        self.assertEqual(
            default_storage_config["BACKEND"], "storages.backends.s3boto3.S3StaticStorage"
        )

        options = default_storage_config["OPTIONS"]
        self.assertEqual(options["access_key"], "test-key")
        self.assertEqual(options["secret_key"], "test-secret")
        self.assertEqual(options["bucket_name"], "test-bucket")
        self.assertEqual(options["default_acl"], "public-read")
        self.assertEqual(options["region_name"], "us-west-2")
        self.assertTrue(options["file_overwrite"])

        private_storage_config = base_settings.STORAGES["private"]
        self.assertEqual(private_storage_config["OPTIONS"]["default_acl"], "private")

        expected_domain = "test-bucket.s3.amazonaws.com"
        self.assertEqual(base_settings.STATIC_URL, f"https://{expected_domain}/static/")
        self.assertEqual(base_settings.MEDIA_URL, f"https://{expected_domain}/media/")

    def test_default_filesystem_storage_configuration(self):
        """Test that filesystem storage is used by default."""
        base_settings = self.reload_settings_module()

        self.assertFalse(base_settings.USE_S3_STORAGE)

        default_storage_config = base_settings.STORAGES["default"]
        self.assertEqual(
            default_storage_config["BACKEND"], "django.core.files.storage.FileSystemStorage"
        )

        self.assertEqual(base_settings.STATIC_URL, "/static/")
        self.assertEqual(base_settings.MEDIA_URL, "/media/")

    @patch.dict(
        os.environ,
        {
            "HAWC_USE_S3_STORAGE": "true",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_STORAGE_BUCKET_NAME": "custom-bucket",
            "AWS_S3_CUSTOM_DOMAIN": "custom.domain.com",
            "AWS_QUERYSTRING_AUTH": "True",
        },
    )
    def test_custom_s3_domain_configuration(self):
        """Test that custom S3 domain is properly configured."""
        base_settings = self.reload_settings_module()

        options = base_settings.STORAGES["default"]["OPTIONS"]
        self.assertEqual(options["custom_domain"], "custom.domain.com")
        self.assertTrue(options["querystring_auth"])

        self.assertEqual(base_settings.STATIC_URL, "https://custom.domain.com/static/")
        self.assertEqual(base_settings.MEDIA_URL, "https://custom.domain.com/media/")


@mock_aws
class S3StorageFunctionalTest(TestCase):
    """Test S3 storage functionality using the actual Django storage system."""

    def setUp(self):
        """Set up mock S3 environment for each test."""
        self.bucket_name = "test-bucket"
        self.conn = boto3.resource("s3", region_name="us-east-1")
        self.conn.create_bucket(Bucket=self.bucket_name)

    def get_storage_settings_from_base_config(self):
        """Get storage settings using the same logic as base.py."""
        storage_options = {
            "access_key": "testing",
            "secret_key": "testing",
            "bucket_name": "test-bucket",
            "default_acl": "public-read",
            "querystring_auth": False,
            "custom_domain": "test-bucket.s3.amazonaws.com",
            "region_name": "us-east-1",
            "use_ssl": True,
            "verify": True,
            "file_overwrite": True,
        }

        return {
            "default": {
                "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
                "OPTIONS": storage_options,
            },
            "staticfiles": {
                "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
                "OPTIONS": storage_options,
            },
            "private": {
                "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
                "OPTIONS": {
                    **storage_options,
                    "default_acl": "private",
                },
            },
        }

    def test_default_storage_write_and_read(self):
        """Test writing and reading files using default storage."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import default_storage

            self.assertIsInstance(default_storage, S3StaticStorage)

            test_content = b"Hello, World!"
            file_name = "test_file.txt"

            saved_name = default_storage.save(file_name, ContentFile(test_content))

            self.assertTrue(default_storage.exists(saved_name))

            with default_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, test_content)

            default_storage.delete(saved_name)
            self.assertFalse(default_storage.exists(saved_name))

    def test_private_storage_write_and_read(self):
        """Test writing and reading files using private storage."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import storages

            private_storage = storages["private"]

            self.assertIsInstance(private_storage, S3StaticStorage)

            test_content = b"Private content"
            file_name = "private_file.txt"

            saved_name = private_storage.save(file_name, ContentFile(test_content))

            self.assertTrue(private_storage.exists(saved_name))

            with private_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, test_content)

            private_storage.delete(saved_name)
            self.assertFalse(private_storage.exists(saved_name))

    def test_file_overwrite_behavior(self):
        """Test that files are overwritten when file_overwrite is True."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import default_storage

            self.assertIsInstance(default_storage, S3StaticStorage)

            file_name = "overwrite_test.txt"

            initial_content = b"Initial content"
            saved_name = default_storage.save(file_name, ContentFile(initial_content))

            new_content = b"New content"
            saved_name_2 = default_storage.save(file_name, ContentFile(new_content))

            self.assertEqual(saved_name, saved_name_2)

            with default_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, new_content)

            default_storage.delete(saved_name)

    def test_storage_url_generation(self):
        """Test that storage generates correct URLs."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import default_storage

            self.assertIsInstance(default_storage, S3StaticStorage)

            test_content = b"Test content"
            file_name = "url_test.txt"

            saved_name = default_storage.save(file_name, ContentFile(test_content))

            url = default_storage.url(saved_name)

            self.assertIn("test-bucket.s3.amazonaws.com", url)
            self.assertIn(saved_name, url)

            default_storage.delete(saved_name)
