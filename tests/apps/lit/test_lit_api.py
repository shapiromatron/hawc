import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client


@pytest.mark.django_db
def test_LiteratureAssessmentViewset_tags(db_keys):
    url = reverse("lit:api:assessment-tags", kwargs=dict(pk=db_keys.assessment_working))
    c = Client()
    assert c.login(email="pm@pm.com", password="pw") is True
    resp = c.get(url).json()
    assert len(resp) == 11
    assert resp[0] == {"id": 2, "depth": 2, "name": "Inclusion", "nested_name": "Inclusion"}
    assert resp[-1] == {"id": 21, "depth": 4, "name": "c", "nested_name": "Exclusion|Tier III|c"}


@pytest.mark.django_db
def test_LiteratureAssessmentViewset_reference_ids(db_keys):
    url = reverse("lit:api:assessment-reference-ids", kwargs=dict(pk=db_keys.assessment_final))
    c = Client()
    assert c.login(email="pm@pm.com", password="pw") is True
    resp = c.get(url).json()
    assert resp == [{"reference_id": 2, "pubmed_id": 29641658, "hero_id": None}]


@pytest.mark.django_db
def test_LiteratureAssessmentViewset_reference_tags(db_keys):
    url = reverse("lit:api:assessment-reference-tags", kwargs=dict(pk=db_keys.assessment_final))
    c = Client()
    assert c.login(email="pm@pm.com", password="pw") is True
    resp = c.get(url).json()
    assert resp == [{"reference_id": 2, "tag_id": 13}]
