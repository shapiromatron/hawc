import os

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertFormError

from hawc.apps.lit import constants, models


@pytest.mark.vcr
@pytest.mark.django_db
def test_pubmed_search(db_keys):
    # Check when searching, the same number of identifiers and refs are
    # created, with refs fully-qualified with identifiers and searches

    # setup
    assessment_pk = db_keys.assessment_working
    client = Client()
    assert client.login(username="pm@hawcproject.org", password="pw") is True
    data = {
        "source": 1,  # PubMed
        "title": "pm search",
        "slug": "pm-search",
        "description": "search description",
        "search_string": "1998 Longstreth health risks ozone depletion",
    }

    # get initial counts
    initial_searches = models.Search.objects.count()
    initial_identifiers = models.Identifiers.objects.count()
    initial_refs = models.Reference.objects.count()

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

    assert models.Search.objects.count() == initial_searches + 1
    i_count = models.Identifiers.objects.count()
    added_ids = i_count - initial_identifiers
    assert added_ids > 200
    assert models.Reference.objects.count() == added_ids + initial_refs

    # make sure all each reference has an identifier
    i_pks = models.Identifiers.objects.values_list("pk", flat=True)
    assert models.Reference.objects.filter(identifiers__in=i_pks).count() == i_count


@pytest.mark.vcr
@pytest.mark.django_db
def test_pubmed_import(db_keys):
    # ensure successful PubMed import
    # setup
    assessment_pk = db_keys.assessment_working
    client = Client()
    assert client.login(username="pm@hawcproject.org", password="pw") is True
    data = {
        "source": 1,  # PubMed
        "title": "pm search",
        "slug": "pm-search",
        "description": "search description",
        "search_string": "1998 Longstreth health risks ozone depletion",
    }

    # get initial counts
    initial_searches = models.Search.objects.count()
    initial_identifiers = models.Identifiers.objects.count()
    initial_refs = models.Reference.objects.count()

    data[
        "search_string"
    ] = "10357793, 20358181, 6355494, 8998951, 3383337, 12209194, 6677511, 11995694, 1632818, 12215663, 3180084, 14727734, 23625783, 11246142, 10485824, 3709451, 2877511, 6143560, 3934796, 8761421"

    # check successful post
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # check new counts
    assert models.Search.objects.count() == initial_searches + 1
    assert models.Identifiers.objects.count() == initial_identifiers + 20
    assert models.Reference.objects.count() == initial_refs + 20

    # make sure all each reference has an identifier
    i_pks = models.Identifiers.objects.values_list("pk", flat=True)
    assert i_pks.count() == initial_identifiers + 20
    assert (
        models.Reference.objects.filter(identifiers__in=i_pks).count() == initial_identifiers + 20
    )


@pytest.mark.vcr
@pytest.mark.django_db
def test_successful_single_hero_id(db_keys):
    """
    Test that a single hero ID can be added. Confirm:
    1) Reference created
    2) Reference associated with search
    3) Reference associated with literature
    """
    # setup
    assessment_pk = db_keys.assessment_working
    client = Client()
    assert client.login(username="pm@hawcproject.org", password="pw") is True
    data = {
        "source": 2,  # HERO
        "title": "example search",
        "slug": "example-search",
        "description": "search description",
        "search_string": "51001",
    }

    # get initial counts
    initial_searches = models.Search.objects.count()
    initial_identifiers = models.Identifiers.objects.count()
    initial_refs = models.Reference.objects.count()

    # check successful post
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # check expected results
    assert models.Search.objects.count() == initial_searches + 1
    assert models.Identifiers.objects.count() == initial_identifiers + 1
    assert models.Reference.objects.count() == initial_refs + 1

    search = models.Search.objects.get(assessment=assessment_pk, title="example search")
    ref = models.Reference.objects.get(title="Effect of thyroid hormone on growth and development")
    ident = models.Identifiers.objects.get(
        unique_id="51001", database=constants.ReferenceDatabase.HERO
    )

    assert ref.searches.all()[0] == search
    assert ref.identifiers.all()[0] == ident


@pytest.mark.vcr
@pytest.mark.django_db
def test_failed_hero_id(db_keys):
    """
    Test that a hero ID that doesn't exist fails gracefully. Confirm:
    1) Search created
    2) No reference created, no literature
    """
    # setup
    assessment_pk = db_keys.assessment_working
    client = Client()
    assert client.login(username="pm@hawcproject.org", password="pw") is True
    data = {
        "source": 2,  # HERO
        "title": "example search",
        "slug": "example-search",
        "description": "search description",
        "search_string": "1200",
    }

    # get initial counts
    initial_searches = models.Search.objects.count()

    # known hero ID that doesn't exist
    data["search_string"] = "9999999"
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)

    assertFormError(
        response,
        "form",
        "search_string",
        "Import failed; the following HERO IDs could not be imported: 9999999",
    )
    assert models.Search.objects.count() == initial_searches


@pytest.mark.vcr
@pytest.mark.django_db
def test_existing_pubmed_hero_add(db_keys):
    """
    Check that search is complete, new identifier is created, but is
    associated with existing PubMed Reference
    """
    # setup
    assessment_pk = db_keys.assessment_working
    client = Client()
    assert client.login(username="pm@hawcproject.org", password="pw") is True
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

    # get initial counts
    initial_searches = models.Search.objects.count()
    initial_identifiers = models.Identifiers.objects.count()
    initial_refs = models.Reference.objects.count()

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
    assert models.Search.objects.count() == initial_searches + 1
    assert models.Identifiers.objects.count() == initial_identifiers + 1
    assert models.Reference.objects.count() == initial_refs + 1

    # build HERO
    data["search_string"] = "1200"
    url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    # assert that search & identifier created but not new reference
    assert models.Search.objects.count() == initial_searches + 2
    assert models.Identifiers.objects.count() == initial_identifiers + 2
    assert models.Reference.objects.count() == initial_refs + 1

    ref = models.Reference.objects.get(authors_short="Longstreth J et al.")
    assert ref.searches.count() == 2
    assert ref.identifiers.count() == 2


class RisFile:
    def __init__(self, fn):
        self.path = fn


@pytest.mark.vcr
@pytest.mark.django_db
def test_ris_import(db_keys):
    # setup
    assessment_id = db_keys.assessment_working
    search = models.Search.objects.create(
        assessment_id=assessment_id,
        search_type="i",
        source=constants.ReferenceDatabase.RIS,
        title="ris",
        slug="ris",
        description="-",
    )
    search.import_file = RisFile(os.path.join(os.path.dirname(__file__), "data/single_ris.txt"))

    # get initial counts
    initial_identifiers = models.Identifiers.objects.count()
    initial_refs = models.Reference.objects.count()

    search.run_new_import()
    ris_ref = models.Reference.objects.filter(
        title="Early alterations in protein and gene expression in rat kidney following bromate exposure"
    ).first()
    assert models.Reference.objects.count() == initial_refs + 1
    assert models.Identifiers.objects.count() == initial_identifiers + 3
    assert ris_ref.identifiers.count() == 3

    assert ris_ref.identifiers.filter(database=constants.ReferenceDatabase.PUBMED).count() == 1
    assert ris_ref.identifiers.filter(database=constants.ReferenceDatabase.RIS).count() == 1
    assert ris_ref.identifiers.filter(database=constants.ReferenceDatabase.DOI).count() == 1

    # assert Pubmed XML content is loaded
    assert (
        "<PubmedArticle>"
        in ris_ref.identifiers.filter(database=constants.ReferenceDatabase.PUBMED).first().content
    )


@pytest.mark.django_db
def test_ris_import_with_existing(db_keys):
    # setup
    assessment_id = db_keys.assessment_working

    # get initial counts
    initial_identifiers = models.Identifiers.objects.count()
    initial_refs = models.Reference.objects.count()

    # ris file should contain the two identifiers above
    search = models.Search.objects.create(
        assessment_id=assessment_id,
        search_type="i",
        source=constants.ReferenceDatabase.RIS,
        title="ris",
        slug="ris",
        description="-",
    )
    search.import_file = RisFile(os.path.join(os.path.dirname(__file__), "data/single_ris.txt"))

    # create existing identifiers
    models.Identifiers.objects.create(
        database=constants.ReferenceDatabase.PUBMED, unique_id="19425233", content=""
    )
    models.Identifiers.objects.create(
        database=constants.ReferenceDatabase.DOI, unique_id="10.1016/j.fct.2009.02.003", content="",
    )
    search.run_new_import()

    ris_ref = models.Reference.objects.filter(
        title="Early alterations in protein and gene expression in rat kidney following bromate exposure"
    ).first()
    assert (
        models.Reference.objects.count() == initial_refs + 1
    )  # only one copy of ref should be made
    assert (
        models.Identifiers.objects.count() == initial_identifiers + 3
    )  # should be 3 different identifiers
    assert ris_ref.identifiers.count() == 3

    # ensure new ones aren't created
    assert ris_ref.identifiers.filter(database=constants.ReferenceDatabase.PUBMED).count() == 1
    assert ris_ref.identifiers.filter(database=constants.ReferenceDatabase.RIS).count() == 1
    assert ris_ref.identifiers.filter(database=constants.ReferenceDatabase.DOI).count() == 1
