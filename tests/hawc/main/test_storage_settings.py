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
        # Store original environment variables
        self.original_environ = os.environ.copy()

    def tearDown(self):
        """Restore original modules and environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_environ)

        # Remove any modules that were added during testing
        modules_to_remove = [
            key
            for key in sys.modules.keys()
            if key not in self.original_modules and key.startswith("hawc.main.settings")
        ]
        for module in modules_to_remove:
            del sys.modules[module]

    def reload_settings_module(self):
        """Reload the settings module to pick up environment changes."""
        # Clear the base settings module from cache
        modules_to_clear = [
            "hawc.main.settings.base",
            "hawc.main.settings",
        ]
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

        # Force reload by importing fresh
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
        # Reload settings with new environment
        base_settings = self.reload_settings_module()

        # Verify USE_S3_STORAGE is correctly set
        self.assertTrue(base_settings.USE_S3_STORAGE)

        # Verify STORAGES configuration
        self.assertIn("default", base_settings.STORAGES)
        self.assertIn("private", base_settings.STORAGES)
        self.assertIn("staticfiles", base_settings.STORAGES)

        # Check default storage configuration
        default_storage_config = base_settings.STORAGES["default"]
        self.assertEqual(
            default_storage_config["BACKEND"], "storages.backends.s3boto3.S3StaticStorage"
        )

        # Check storage options
        options = default_storage_config["OPTIONS"]
        self.assertEqual(options["access_key"], "test-key")
        self.assertEqual(options["secret_key"], "test-secret")
        self.assertEqual(options["bucket_name"], "test-bucket")
        self.assertEqual(options["default_acl"], "public-read")
        self.assertEqual(options["region_name"], "us-west-2")
        self.assertTrue(options["file_overwrite"])

        # Check private storage has private ACL
        private_storage_config = base_settings.STORAGES["private"]
        self.assertEqual(private_storage_config["OPTIONS"]["default_acl"], "private")

        # Check URLs are set correctly
        expected_domain = "test-bucket.s3.amazonaws.com"
        self.assertEqual(base_settings.STATIC_URL, f"https://{expected_domain}/static/")
        self.assertEqual(base_settings.MEDIA_URL, f"https://{expected_domain}/media/")

    def test_default_filesystem_storage_configuration(self):
        """Test that filesystem storage is used by default."""
        # Reload settings with new environment
        base_settings = self.reload_settings_module()

        # Verify USE_S3_STORAGE is correctly set
        self.assertFalse(base_settings.USE_S3_STORAGE)

        # Verify STORAGES configuration uses filesystem
        default_storage_config = base_settings.STORAGES["default"]
        self.assertEqual(
            default_storage_config["BACKEND"], "django.core.files.storage.FileSystemStorage"
        )

        # Check that URLs are set for local files
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
        # Reload settings with new environment
        base_settings = self.reload_settings_module()

        # Check custom domain is used
        options = base_settings.STORAGES["default"]["OPTIONS"]
        self.assertEqual(options["custom_domain"], "custom.domain.com")
        self.assertTrue(options["querystring_auth"])

        # Check URLs use custom domain
        self.assertEqual(base_settings.STATIC_URL, "https://custom.domain.com/static/")
        self.assertEqual(base_settings.MEDIA_URL, "https://custom.domain.com/media/")


@mock_aws
class S3StorageFunctionalTest(TestCase):
    """Test S3 storage functionality using the actual Django storage system."""

    def setUp(self):
        """Set up mock S3 environment for each test."""
        # Create mock S3 bucket
        self.bucket_name = "test-bucket"
        self.conn = boto3.resource("s3", region_name="us-east-1")
        self.conn.create_bucket(Bucket=self.bucket_name)

    def get_storage_settings_from_base_config(self):
        """Get storage settings using the same logic as base.py."""
        # This mimics the logic in your base.py file
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
        # Use the same configuration logic as base.py
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import default_storage

            # Verify we're using S3 storage (this tests the integration)
            self.assertIsInstance(default_storage, S3StaticStorage)

            # Write a file
            test_content = b"Hello, World!"
            file_name = "test_file.txt"

            saved_name = default_storage.save(file_name, ContentFile(test_content))

            # Verify file exists
            self.assertTrue(default_storage.exists(saved_name))

            # Read the file back
            with default_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, test_content)

            # Clean up
            default_storage.delete(saved_name)
            self.assertFalse(default_storage.exists(saved_name))

    def test_private_storage_write_and_read(self):
        """Test writing and reading files using private storage."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import storages

            private_storage = storages["private"]

            # Verify we're using S3 storage
            self.assertIsInstance(private_storage, S3StaticStorage)

            # Write a file
            test_content = b"Private content"
            file_name = "private_file.txt"

            saved_name = private_storage.save(file_name, ContentFile(test_content))

            # Verify file exists
            self.assertTrue(private_storage.exists(saved_name))

            # Read the file back
            with private_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, test_content)

            # Clean up
            private_storage.delete(saved_name)
            self.assertFalse(private_storage.exists(saved_name))

    def test_file_overwrite_behavior(self):
        """Test that files are overwritten when file_overwrite is True."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import default_storage

            # Verify we're using S3 storage
            self.assertIsInstance(default_storage, S3StaticStorage)

            file_name = "overwrite_test.txt"

            # Write initial content
            initial_content = b"Initial content"
            saved_name = default_storage.save(file_name, ContentFile(initial_content))

            # Overwrite with new content
            new_content = b"New content"
            saved_name_2 = default_storage.save(file_name, ContentFile(new_content))

            # Should be the same filename since overwrite is enabled
            self.assertEqual(saved_name, saved_name_2)

            # Read back and verify new content
            with default_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, new_content)

            # Clean up
            default_storage.delete(saved_name)

    def test_storage_url_generation(self):
        """Test that storage generates correct URLs."""
        with override_settings(STORAGES=self.get_storage_settings_from_base_config()):
            from django.core.files.storage import default_storage

            # Verify we're using S3 storage
            self.assertIsInstance(default_storage, S3StaticStorage)

            # Save a file
            test_content = b"Test content"
            file_name = "url_test.txt"

            saved_name = default_storage.save(file_name, ContentFile(test_content))

            # Get URL
            url = default_storage.url(saved_name)

            # Should contain the custom domain
            self.assertIn("test-bucket.s3.amazonaws.com", url)
            self.assertIn(saved_name, url)

            # Clean up
            default_storage.delete(saved_name)


@mock_aws
class S3StorageIntegrationTest(TestCase):
    """Integration tests that combine configuration and functionality testing."""

    def setUp(self):
        """Set up mock S3 environment for each test."""
        self.bucket_name = "integration-test-bucket"
        self.conn = boto3.resource("s3", region_name="us-east-1")
        self.conn.create_bucket(Bucket=self.bucket_name)

        # Store original modules for cleanup
        self.original_modules = sys.modules.copy()

    def tearDown(self):
        """Clean up modules."""
        # Remove any modules that were added during testing
        modules_to_remove = [
            key
            for key in sys.modules.keys()
            if key not in self.original_modules and key.startswith("hawc.main.settings")
        ]
        for module in modules_to_remove:
            del sys.modules[module]

    def clear_storage_cache(self):
        """Clear Django's storage cache to ensure fresh initialization."""
        from django.core.files import storage

        # Clear the storage cache
        if hasattr(storage, "_storages"):
            storage._storages.clear()

        # Clear the default storage cache
        if hasattr(storage, "_default_storage"):
            delattr(storage, "_default_storage")

    @patch.dict(
        os.environ,
        {
            "HAWC_USE_S3_STORAGE": "true",
            "AWS_ACCESS_KEY_ID": "integration-test",
            "AWS_SECRET_ACCESS_KEY": "integration-test",
            "AWS_STORAGE_BUCKET_NAME": "integration-test-bucket",
        },
    )
    def test_end_to_end_s3_configuration_and_usage(self):
        """Test that environment variables properly configure S3 and it works end-to-end."""
        # Step 1: Test that base.py correctly configures S3 from environment
        if "hawc.main.settings.base" in sys.modules:
            del sys.modules["hawc.main.settings.base"]

        from hawc.main.settings import base

        # Verify configuration is correct
        self.assertTrue(base.USE_S3_STORAGE)
        self.assertEqual(
            base.STORAGES["default"]["BACKEND"], "storages.backends.s3boto3.S3StaticStorage"
        )
        self.assertEqual(
            base.STORAGES["default"]["OPTIONS"]["bucket_name"], "integration-test-bucket"
        )

        # Step 2: Test that Django actually uses this configuration
        with override_settings(STORAGES=base.STORAGES):
            # Clear storage cache to ensure fresh initialization
            self.clear_storage_cache()

            from django.core.files.storage import default_storage

            # Verify we get the S3 backend
            self.assertIsInstance(default_storage, S3StaticStorage)
            self.assertEqual(default_storage.bucket_name, "integration-test-bucket")

            # Step 3: Test that it actually works for file operations
            test_content = b"Integration test content"
            file_name = "integration_test.txt"

            saved_name = default_storage.save(file_name, ContentFile(test_content))
            self.assertTrue(default_storage.exists(saved_name))

            with default_storage.open(saved_name) as f:
                content = f.read()

            self.assertEqual(content, test_content)

            # Clean up
            default_storage.delete(saved_name)
            self.assertFalse(default_storage.exists(saved_name))
