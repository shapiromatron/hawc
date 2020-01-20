import os

import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client
from pytest_django.asserts import assertFormError

from hawc.apps.lit import constants, models


@pytest.mark.django_db
def test_clean_import_string(assessment_data):
    assessment_pk = assessment_data["assessment"]["assessment_working"].id
    client = Client()
    assert client.login(username="pm@pm.com", password="pw") is True
    data = {
        "source": 2,
        "title": "example search",
        "slug": "example-search",
        "description": "search description",
        "search_string": "1234, 1235, 12345",
    }

    # comma-separating checks
    failed_strings = [
        "string",
        "123, number, 1234",
        "-123",
        "123,,1234",
        "123, , 1234",
    ]
    for search_string in failed_strings:
        data["search_string"] = search_string
        response = client.post(reverse("lit:import_new", kwargs={"pk": assessment_pk}), data)
        assertFormError(
            response,
            "form",
            "search_string",
            "Please enter a comma-separated list of numeric IDs.",
        )

    # ID uniqueness-check
    data["search_string"] = "123, 123"
    response = client.post(reverse("lit:import_new", kwargs={"pk": assessment_pk}), data)
    assertFormError(response, "form", "search_string", "IDs must be unique.")


@pytest.mark.django_db
def test_pubmed_search(assessment_data):
    # Check when searching, the same number of identifiers and refs are
    # created, with refs fully-qualified with identifiers and searches

    # setup
    assessment_pk = assessment_data["assessment"]["assessment_working"].id
    client = Client()
    assert client.login(username="pm@pm.com", password="pw") is True
    data = {
        "source": 1,  # PubMed
        "title": "pm search",
        "slug": "pm-search",
        "description": "search description",
        "search_string": "1998 Longstreth health risks ozone depletion",
    }

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 2
    assert models.Identifiers.objects.count() == 0

    # term returns 200+ literature
    data[
        "search_string"
    ] = """(monomethyl OR MEP OR mono-n-butyl OR MBP OR mono (3-carboxypropyl) OR mcpp OR monobenzyl OR mbzp OR mono-isobutyl OR mibp OR mono (2-ethylhexyl) OR mono (2-ethyl-5-oxohexyl) OR meoph OR mono (2-ethyl-5-carboxypentyl) OR mecpp OR mepp OR mono (2-ethyl-5-hydroxyhexyl) OR mehp OR mono (2-ethyl-5-oxyhexyl) OR mono (2-ethyl-4-hydroxyhexyl) OR mono (2-ethyl-4-oxyhexyl) OR mono (2-carboxymethyl) OR mmhp OR mehp OR dehp OR 2-ethylhexanol OR (phthalic acid)) AND (liver OR hepato* OR hepat*) AND ((cell proliferation) OR (cell growth) OR (dna replication) OR (dna synthesis) OR (replicative dna synthesis) OR mitosis OR (cell division) OR (growth response) OR hyperplasia OR hepatomegaly) AND (mouse OR rat OR hamster OR rodent OR murine OR Mus musculus or Rattus)"""

    # check successful post
    url = reverse("lit:search_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # run search
    search = models.Search.objects.latest()
    url = reverse("lit:search_query", kwargs={"pk": assessment_pk, "slug": search.slug})
    response = client.get(url, data)
    assert response.status_code in [200, 302]

    assert models.Search.objects.count() == 3
    i_count = models.Identifiers.objects.count()
    assert i_count > 200
    assert models.Reference.objects.count() == i_count

    # make sure all each reference has an identifier
    i_pks = models.Identifiers.objects.values_list("pk", flat=True)
    assert models.Reference.objects.filter(identifiers__in=i_pks).count() == i_count

    # make sure all references associated with search
    assert models.Reference.objects.filter(searches=search).count() == i_count


@pytest.mark.django_db
def test_pubmed_import(assessment_data):
    # ensure successful PubMed import
    # setup
    assessment_pk = assessment_data["assessment"]["assessment_working"].id
    client = Client()
    assert client.login(username="pm@pm.com", password="pw") is True
    data = {
        "source": 1,  # PubMed
        "title": "pm search",
        "slug": "pm-search",
        "description": "search description",
        "search_string": "1998 Longstreth health risks ozone depletion",
    }

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 2
    assert models.Identifiers.objects.count() == 0

    data[
        "search_string"
    ] = "10357793, 20358181, 6355494, 8998951, 3383337, 12209194, 6677511, 11995694, 1632818, 12215663, 3180084, 14727734, 23625783, 11246142, 10485824, 3709451, 2877511, 6143560, 3934796, 8761421"

    # check successful post
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # check new counts
    assert models.Reference.objects.count() == 20
    assert models.Search.objects.count() == 3
    assert models.Identifiers.objects.count() == 20

    # make sure all each reference has an identifier
    i_pks = models.Identifiers.objects.values_list("pk", flat=True)
    search = models.Search.objects.latest()
    assert i_pks.count() == 20
    assert models.Reference.objects.filter(identifiers__in=i_pks).count() == 20

    # make sure all references associated with search
    assert models.Reference.objects.filter(searches=search).count() == 20


@pytest.mark.skip(reason="TODO: fix")
@pytest.mark.django_db
def test_successful_single_hero_id(assessment_data):
    """
    Test that a single hero ID can be added. Confirm:
    1) Reference created
    2) Reference associated with search
    3) Reference associated with literature
    """
    # setup
    assessment_pk = assessment_data["assessment"]["assessment_working"].id
    client = Client()
    assert client.login(username="pm@pm.com", password="pw") is True
    data = {
        "source": 2,  # HERO
        "title": "example search",
        "slug": "example-search",
        "description": "search description",
        "search_string": "1200",
    }

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 2
    assert models.Identifiers.objects.count() == 0

    # check successful post
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # check expected results
    assert models.Search.objects.count() == 3
    assert models.Identifiers.objects.count() == 1
    assert models.Reference.objects.count() == 1
    ref = models.Reference.objects.all()[0]

    search = models.Search.objects.get(assessment=assessment_pk, title="example search")
    ident = models.Identifiers.objects.all()[0]
    assert ref.searches.all()[0] == search
    assert ref.identifiers.all()[0] == ident


@pytest.mark.django_db
def test_failed_hero_id(assessment_data):
    """
    Test that a hero ID that doesn't exist fails gracefully. Confirm:
    1) Search created
    2) No reference created, no literature
    """
    # setup
    assessment_pk = assessment_data["assessment"]["assessment_working"].id
    client = Client()
    assert client.login(username="pm@pm.com", password="pw") is True
    data = {
        "source": 2,  # HERO
        "title": "example search",
        "slug": "example-search",
        "description": "search description",
        "search_string": "1200",
    }

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 2  # manual imports
    assert models.Identifiers.objects.count() == 0

    # known hero ID that doesn't exist
    data["search_string"] = "9999999"
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)

    # check completion as as expected
    assert response.status_code in [200, 302]
    assert models.Search.objects.count() == 3
    assert models.Reference.objects.count() == 0
    assert models.Identifiers.objects.count() == 0


@pytest.mark.skip(reason="TODO: fix")
@pytest.mark.django_db
def test_existing_pubmed_hero_add(assessment_data):
    """
    Check that search is complete, new identifier is created, but is
    associated with existing PubMed Reference
    """
    # setup
    assessment_pk = assessment_data["assessment"]["assessment_working"].id
    client = Client()
    assert client.login(username="pm@pm.com", password="pw") is True
    data = {
        "source": 2,  # HERO
        "title": "example search",
        "slug": "example-search",
        "description": "search description",
        "search_string": "1200",
    }
    pm_data = {
        "source": 1,  # PubMed
        "title": "pm search",
        "slug": "pm-search",
        "description": "search description",
        "search_string": "1998 Longstreth health risks ozone depletion",
    }

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 2  # manual imports
    assert models.Identifiers.objects.count() == 0

    # build PubMed
    url = reverse("lit:search_new", kwargs={"pk": assessment_pk})
    response = client.post(url, pm_data)
    assert response.status_code in [200, 302]

    # Run PubMed Query
    url_run_query = reverse(
        "lit:search_query", kwargs={"pk": assessment_pk, "slug": pm_data["slug"]},
    )
    response = client.get(url_run_query)
    assert response.status_code in [200, 302]

    # assert that one object was created
    assert models.Reference.objects.count() == 1
    assert models.Search.objects.count() == 3
    assert models.Identifiers.objects.count() == 1

    # build HERO
    data["search_string"] = "1200"
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # assert that search & identifier created but not new reference
    assert models.Search.objects.count() == 4
    assert models.Identifiers.objects.count() == 2
    assert models.Reference.objects.count() == 1

    ref = models.Reference.objects.all()[0]
    assert ref.searches.count() == 2
    assert ref.identifiers.count() == 2


class TestFile:
    def __init__(self, fn):
        self.path = fn


@pytest.mark.django_db
def test_ris_import(assessment_data):
    # setup
    assessment = assessment_data["assessment"]["assessment_working"]
    search = models.Search.objects.create(
        assessment_id=assessment.id,
        search_type="i",
        source=constants.RIS,
        title="ris",
        slug="ris",
        description="-",
    )
    search.import_file = TestFile(os.path.join(os.path.dirname(__file__), "data/single_ris.txt"))

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 3
    assert models.Identifiers.objects.count() == 0

    search.run_new_import()
    assert models.Reference.objects.count() == 1
    assert models.Identifiers.objects.count() == 3
    assert models.Reference.objects.first().identifiers.count() == 3

    assert models.Identifiers.objects.filter(database=constants.PUBMED).count() == 1
    assert models.Identifiers.objects.filter(database=constants.RIS).count() == 1
    assert models.Identifiers.objects.filter(database=constants.DOI).count() == 1

    # assert Pubmed XML content is loaded
    assert (
        "<PubmedArticle>"
        in models.Identifiers.objects.filter(database=constants.PUBMED).first().content
    )


@pytest.mark.django_db
def test_ris_import_with_existing(assessment_data):
    # setup
    assessment = assessment_data["assessment"]["assessment_working"]
    search = models.Search.objects.create(
        assessment_id=assessment.id,
        search_type="i",
        source=constants.RIS,
        title="ris",
        slug="ris",
        description="-",
    )
    search.import_file = TestFile(os.path.join(os.path.dirname(__file__), "data/single_ris.txt"))

    # check initially blank
    assert models.Reference.objects.count() == 0
    assert models.Search.objects.count() == 3
    assert models.Identifiers.objects.count() == 0

    # create existing identifiers
    models.Identifiers.objects.create(
        database=constants.PUBMED, unique_id="19425233", content="None"
    )
    models.Identifiers.objects.create(
        database=constants.DOI, unique_id="10.1016/j.fct.2009.02.003", content="None",
    )

    search.run_new_import()
    assert models.Reference.objects.count() == 1
    assert models.Identifiers.objects.count() == 3
    assert models.Reference.objects.first().identifiers.count() == 3

    # ensure new ones aren't created
    assert models.Identifiers.objects.filter(database=constants.PUBMED).count() == 1
    assert models.Identifiers.objects.filter(database=constants.RIS).count() == 1
    assert models.Identifiers.objects.filter(database=constants.DOI).count() == 1
