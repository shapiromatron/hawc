import pytest
from django.test.client import Client
from django.urls import reverse

from hawc.apps.assessment.models import Assessment


class TestAssessmentClearCache:
    @pytest.mark.django_db
    def test_permissions(self, db_keys):
        url = Assessment.objects.get(id=db_keys.assessment_working).get_clear_cache_url()

        # test failures
        for client in ["rev@rev.com", None]:
            c = Client()
            if client:
                assert c.login(username=client, password="pw") is True
            response = c.get(url)
            assert response.status_code == 403

        # test successes
        for client in ["pm@pm.com", "team@team.com"]:
            c = Client()
            if client:
                assert c.login(username=client, password="pw") is True
            # this is success behavior in test environment w/o redis - TODO improve?
            with pytest.raises(NotImplementedError):
                response = c.get(url)

    @pytest.mark.django_db
    def test_functionality(self, db_keys):
        url = Assessment.objects.get(id=db_keys.assessment_working).get_clear_cache_url()
        c = Client()
        assert c.login(username="pm@pm.com", password="pw") is True
        # this is success behavior in test environment w/o redis - TODO improve?
        with pytest.raises(NotImplementedError):
            c.get(url)


@pytest.mark.django_db
class TestAboutPage:
    def test_counts(self):
        client = Client()
        url = reverse("about")
        response = client.get(url)
        assert "counts" in response.context
        assert response.context["counts"]["assessments"] == 3
        assert response.context["counts"]["users"] == 5
