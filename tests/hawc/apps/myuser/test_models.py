import pytest
from django.core import mail
from django.test.client import RequestFactory

from hawc.apps.myuser.models import HAWCUser


@pytest.mark.django_db
class TestMyUser:
    def test_can_create_assessments(self, settings):
        team = HAWCUser.objects.get(email="team@hawcproject.org")
        admin = HAWCUser.objects.get(email="admin@hawcproject.org")

        settings.ANYONE_CAN_CREATE_ASSESSMENTS = True
        assert team.can_create_assessments() is True
        assert team.groups.filter(name=HAWCUser.CAN_CREATE_ASSESSMENTS).exists() is False

        settings.ANYONE_CAN_CREATE_ASSESSMENTS = False
        assert admin.can_create_assessments() is True
        assert team.can_create_assessments() is False

        group, _ = team.groups.get_or_create(name=HAWCUser.CAN_CREATE_ASSESSMENTS)
        team.groups.add(group)
        assert team.can_create_assessments() is True

        # cleanup; required for test suite
        group.delete()

    def test_welcome_email(self):
        team = HAWCUser.objects.get(email="team@hawcproject.org")
        team.send_welcome_email()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Welcome to HAWC!"

    def test_send_email_verification(self):
        team = HAWCUser.objects.get(email="team@hawcproject.org")

        rf = RequestFactory()
        request = rf.get("/")
        team.send_email_verification(request)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "HAWC - email verification"
