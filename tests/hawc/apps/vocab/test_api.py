import pytest
from django.urls import reverse
from model_bakery.baker import make
from rest_framework.test import APIClient

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.vocab.constants import VocabularyNamespace, VocabularyTermType
from hawc.apps.vocab.models import Term


def client_for_user(**kwargs):
    user = make(
        HAWCUser, email=kwargs.pop("email", "vocab-api@example.com"), is_active=True, **kwargs
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_ehv_actions_and_filters_use_baked_data():
    term = make(
        Term,
        namespace=VocabularyNamespace.EHV,
        type=VocabularyTermType.endpoint_name,
        name="Unique Endpoint",
        uid=8800,
    )
    client = client_for_user()
    assert client.get(reverse("vocab:api:ehv-endpoint-name") + "?term=Unique").json() == [
        {"id": term.id, "name": term.name}
    ]
    assert client.get(reverse("vocab:api:ehv-endpoint-name") + "?term=missing").json() == []
    anonymous = APIClient()
    assert anonymous.get(reverse("vocab:api:ehv-system")).status_code == 403
    assert anonymous.get(reverse("vocab:api:toxrefdb-system")).status_code == 403
    assert client.get(reverse("vocab:api:ehv-system")).status_code == 200
    assert client.get(reverse("vocab:api:toxrefdb-system")).status_code == 200


@pytest.mark.django_db
def test_nested_and_uids_endpoints():
    make(
        Term,
        namespace=VocabularyNamespace.EHV,
        type=VocabularyTermType.system,
        uid=8810,
        name="nested system",
    )
    client = client_for_user()
    response = client.get(reverse("vocab:api:ehv-nested") + "?format=csv")
    assert response.status_code == 200
    assert response.content
    response = client.get(reverse("vocab:api:term-uids"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_term_bulk_create_requires_admin_and_saves_baked_payload():
    client = client_for_user(is_staff=True, is_superuser=True)
    response = client.post(
        reverse("vocab:api:term-bulk-create"),
        [{"uid": 8820, "name": "bulk", "type": 1}],
        format="json",
    )
    assert response.status_code == 201
    assert Term.objects.filter(uid=8820, name="bulk").exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action,type_value", [("organ", 2), ("effect", 3), ("effect-subtype", 4), ("endpoint-name", 5)]
)
def test_all_ehv_actions_and_parent_filter(action, type_value):
    parent = make(Term, namespace=1, type=1, name=f"parent-{action}")
    other_parent = make(Term, namespace=1, type=1, name=f"other-parent-{action}")
    term = make(Term, namespace=1, type=type_value, parent=parent, name=f"unique-{action}")
    make(Term, namespace=1, type=type_value, parent=other_parent, name=f"unique-{action}")
    client = client_for_user(email=f"{action}@example.com")
    url = reverse(f"vocab:api:ehv-{action}") + f"?term=unique&parent={parent.id}"
    assert client.get(url).json() == [{"id": term.id, "name": term.name}]


@pytest.mark.django_db
def test_tox_nested_and_endpoint_lookup_and_related_entity():
    system = make(Term, namespace=2, type=1, name="tox lookup system")
    effect = make(Term, namespace=2, type=3, parent=system, name="tox lookup effect")
    subtype = make(Term, namespace=2, type=4, parent=effect, name="tox lookup subtype")
    endpoint = make(Term, namespace=2, type=5, parent=subtype, name="tox lookup endpoint")
    client = client_for_user(email="tox-api@example.com")
    assert client.get(reverse("vocab:api:toxrefdb-nested") + "?format=csv").status_code == 200
    lookup = client.get(reverse("vocab:api:toxrefdb-endpoint-name-lookup", args=[endpoint.id]))
    assert lookup.status_code == 200 and lookup.json()["name"] == endpoint.name
    related = client.post(
        reverse("vocab:api:toxrefdb-related-entity", args=[endpoint.id]),
        {"ontology": 1, "uid": "C8801", "notes": "n"},
        format="json",
    )
    assert related.status_code == 201


@pytest.mark.django_db
def test_endpoint_lookup_not_found_and_bulk_update():
    client = client_for_user(email="admin-api@example.com", is_staff=True, is_superuser=True)
    missing = client.get(reverse("vocab:api:ehv-endpoint-name-lookup", args=[999999]))
    assert missing.status_code == 404
    term = make(Term, uid=8830, name="before bulk")
    response = client.patch(
        reverse("vocab:api:term-bulk-update"),
        [{"id": term.id, "name": "after bulk"}],
        format="json",
    )
    assert response.status_code == 200 and response.json()[0]["name"] == "after bulk"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("payload", "method"),
    [
        ({"id": "existing"}, "post"),
        ({"type": 99}, "post"),
        ({"id": "missing", "name": "updated"}, "patch"),
    ],
)
def test_bulk_validation_rejects_invalid_payloads(payload, method):
    client = client_for_user(email="validation-admin@example.com", is_staff=True, is_superuser=True)
    existing = make(Term, uid=8840, name="existing")
    if payload.get("id") == "existing":
        payload["id"] = existing.pk
    elif payload.get("id") == "missing":
        payload["id"] = existing.pk + 100000
    if method == "post":
        payload.setdefault("uid", 8841)
        payload.setdefault("name", "invalid")
        url = reverse("vocab:api:term-bulk-create")
        response = client.post(url, [payload], format="json")
    else:
        url = reverse("vocab:api:term-bulk-update")
        response = client.patch(url, [payload], format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_anonymous_and_non_admin_bulk_permissions():
    url = reverse("vocab:api:term-bulk-create")
    assert APIClient().post(url, [], format="json").status_code == 403
    assert (
        client_for_user(email="nonadmin@example.com").post(url, [], format="json").status_code
        == 403
    )
