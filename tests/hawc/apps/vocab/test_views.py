import pytest
from django.urls import reverse
from model_bakery.baker import make
from rest_framework.test import APIClient
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType
from hawc.apps.vocab.models import Term

@pytest.mark.django_db
@pytest.mark.parametrize("name", ["vocab:ehv-browse", "vocab:toxrefdb-browse"])
def test_browse_views_return_200(name):
    make(HAWCUser, email="vocab-view@example.com", is_active=True)
    make(Term, namespace=VocabularyNamespace.EHV, type=VocabularyTermType.system, uid=8700)
    client = APIClient()
    assert client.get(reverse(name)).status_code == 200
