import pytest

from hawc.apps.assessment.actions.search import search_studies, search_visuals
from hawc.apps.assessment.models import Assessment

from ...test_utils import get_user


@pytest.mark.django_db
def test_search_studies():
    qs = search_studies(query="biesemeier")
    assert qs.count() == 0

    qs = search_studies(query="biesemeier", all_public=True)
    assert qs.count() == 1

    qs = search_studies(query="biesemeier", public=Assessment.objects.filter(id=2))
    assert qs.count() == 1

    pm = get_user("pm")
    qs = search_studies(query="biesemeier", all_internal=True, user=pm)
    assert qs.count() == 1

    pm = get_user("pm")
    qs = search_studies(query="biesemeier", internal=Assessment.objects.filter(id=2), user=pm)
    assert qs.count() == 1


@pytest.mark.django_db
def test_search_visuals():
    qs = search_visuals(query="plotly")
    assert qs.count() == 0

    qs = search_visuals(query="plotly", all_public=True)
    assert qs.count() == 1

    qs = search_visuals(query="plotly", public=Assessment.objects.filter(id=2))
    assert qs.count() == 1

    pm = get_user("pm")
    qs = search_visuals(query="plotly", all_internal=True, user=pm)
    assert qs.count() == 1

    qs = search_visuals(query="plotly", internal=Assessment.objects.filter(id=2), user=pm)
    assert qs.count() == 1
