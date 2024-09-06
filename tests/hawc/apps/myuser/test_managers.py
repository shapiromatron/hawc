import pytest

from hawc.apps.myuser.models import HAWCUser


@pytest.mark.django_db
class TestHAWCMgr:
    def test_create_user(self):
        user = HAWCUser.objects.create_user(email="foo@bar.com", password="foo")
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.password != "foo"  # ensure it's hashed/salted  # noqa: S105

    def test_create_superuser(self):
        user = HAWCUser.objects.create_superuser(email="foo2@bar.com", password="foo")
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.password != "foo"  # ensure it's hashed/salted  # noqa: S105
