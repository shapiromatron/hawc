import pytest

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
