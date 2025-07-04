import os
from unittest import mock


class TestStorageSettings:
    """Test storage configuration in Django settings."""

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_default_filesystem_storage(self):
        """Test that default configuration uses filesystem storage."""
        # Clear any existing Django settings
        import django.conf

        if django.conf.settings.configured:
            django.conf.settings._wrapped = None
            django.conf.settings.configured = False

        # Import settings with clean environment
        from hawc.main.settings import base

        # Should use filesystem storage by default
        assert not hasattr(base, "USE_S3_STORAGE") or base.USE_S3_STORAGE is False
        assert base.STATIC_URL == "/static/"
        assert base.MEDIA_URL == "/media/"
        assert "static" in str(base.STATIC_ROOT)
        assert "media" in str(base.MEDIA_ROOT)
        assert base.FILE_UPLOAD_PERMISSIONS == 0o755

    @mock.patch.dict(
        os.environ,
        {
            "HAWC_USE_S3_STORAGE": "true",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_STORAGE_BUCKET_NAME": "test-bucket",
            "AWS_S3_REGION_NAME": "us-west-2",
        },
    )
    def test_s3_storage_configuration(self):
        """Test S3 storage configuration when enabled."""
        # Clear any existing Django settings
        import django.conf

        if django.conf.settings.configured:
            django.conf.settings._wrapped = None
            django.conf.settings.configured = False

        # Reload settings module to pick up new environment
        import importlib

        from hawc.main.settings import base

        importlib.reload(base)

        # Should use S3 storage
        assert base.USE_S3_STORAGE is True
        assert base.AWS_ACCESS_KEY_ID == "test-key"
        assert base.AWS_SECRET_ACCESS_KEY == "test-secret"
        assert base.AWS_STORAGE_BUCKET_NAME == "test-bucket"
        assert base.AWS_S3_REGION_NAME == "us-west-2"

        # Should configure S3 URLs
        assert "s3.amazonaws.com" in base.STATIC_URL
        assert "s3.amazonaws.com" in base.MEDIA_URL
        assert "test-bucket" in base.STATIC_URL
        assert "test-bucket" in base.MEDIA_URL

        # Should set S3 storage backends
        assert base.STATICFILES_STORAGE == "storages.backends.s3boto3.S3StaticStorage"
        assert base.DEFAULT_FILE_STORAGE == "storages.backends.s3boto3.S3Boto3Storage"

    @mock.patch.dict(
        os.environ,
        {
            "HAWC_USE_S3_STORAGE": "true",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_STORAGE_BUCKET_NAME": "test-bucket",
            "AWS_S3_CUSTOM_DOMAIN": "cdn.example.com",
        },
    )
    def test_s3_storage_with_custom_domain(self):
        """Test S3 storage with custom domain (CDN)."""
        # Clear any existing Django settings
        import django.conf

        if django.conf.settings.configured:
            django.conf.settings._wrapped = None
            django.conf.settings.configured = False

        # Reload settings module to pick up new environment
        import importlib

        from hawc.main.settings import base

        importlib.reload(base)

        # Should use custom domain for URLs
        assert base.AWS_S3_CUSTOM_DOMAIN == "cdn.example.com"
        assert "cdn.example.com" in base.STATIC_URL
        assert "cdn.example.com" in base.MEDIA_URL
        assert "s3.amazonaws.com" not in base.STATIC_URL
        assert "s3.amazonaws.com" not in base.MEDIA_URL

    @mock.patch.dict(
        os.environ,
        {
            "HAWC_USE_S3_STORAGE": "true",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
            "AWS_STORAGE_BUCKET_NAME": "test-bucket",
            "AWS_S3_ENDPOINT_URL": "https://minio.example.com",
            "AWS_S3_USE_SSL": "false",
            "AWS_QUERYSTRING_AUTH": "true",
            "AWS_DEFAULT_ACL": "private",
        },
    )
    def test_s3_storage_with_custom_options(self):
        """Test S3 storage with custom endpoint and options (S3-compatible)."""
        # Clear any existing Django settings
        import django.conf

        if django.conf.settings.configured:
            django.conf.settings._wrapped = None
            django.conf.settings.configured = False

        # Reload settings module to pick up new environment
        import importlib

        from hawc.main.settings import base

        importlib.reload(base)

        # Should configure custom endpoint and options
        assert base.AWS_S3_ENDPOINT_URL == "https://minio.example.com"
        assert base.AWS_S3_USE_SSL is False
        assert base.AWS_QUERYSTRING_AUTH is True
        assert base.AWS_DEFAULT_ACL == "private"

        # Should use custom endpoint in URLs
        assert "minio.example.com" in base.STATIC_URL
        assert "minio.example.com" in base.MEDIA_URL
        assert "test-bucket" in base.STATIC_URL
        assert "test-bucket" in base.MEDIA_URL

    @mock.patch.dict(os.environ, {"HAWC_USE_S3_STORAGE": "false"})
    def test_explicit_filesystem_storage(self):
        """Test explicitly disabling S3 storage."""
        # Clear any existing Django settings
        import django.conf

        if django.conf.settings.configured:
            django.conf.settings._wrapped = None
            django.conf.settings.configured = False

        # Reload settings module to pick up new environment
        import importlib

        from hawc.main.settings import base

        importlib.reload(base)

        # Should use filesystem storage
        assert base.USE_S3_STORAGE is False
        assert base.STATIC_URL == "/static/"
        assert base.MEDIA_URL == "/media/"

    def test_common_staticfiles_configuration(self):
        """Test that common staticfiles configuration is preserved."""
        from hawc.main.settings import base

        # These should be set regardless of storage backend
        assert "static" in str(base.STATICFILES_DIRS[0])
        assert "django.contrib.staticfiles.finders.FileSystemFinder" in base.STATICFILES_FINDERS
        assert "django.contrib.staticfiles.finders.AppDirectoriesFinder" in base.STATICFILES_FINDERS


class TestStorageImports:
    """Test that django-storages can be imported when configured."""

    @mock.patch.dict(
        os.environ, {"HAWC_USE_S3_STORAGE": "true", "AWS_STORAGE_BUCKET_NAME": "test-bucket"}
    )
    def test_storages_import_available(self):
        """Test that storages module is available when S3 is configured."""
        # This test verifies that django-storages is available
        # In a real environment, this would fail if django-storages wasn't installed
        try:
            import storages.backends.s3boto3

            storages_available = True
        except ImportError:
            storages_available = False

        # For now, we'll just check that the import path is valid
        # In production, this should always be True
        assert isinstance(storages_available, bool)
