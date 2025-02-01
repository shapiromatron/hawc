import os

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertFormError

from hawc.apps.lit import constants, models


@pytest.mark.vcr
@pytest.mark.django_db
class TestPubmed:
    def test_search(self, db_keys):
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
        pm_ids_qs = models.Identifiers.objects.filter(database=constants.ReferenceDatabase.PUBMED)
        doi_ids_qs = models.Identifiers.objects.filter(database=constants.ReferenceDatabase.DOI)

        initial_refs = models.Reference.objects.count()
        n_pm_ids = pm_ids_qs.count()
        n_doi_ids_qs = doi_ids_qs.count()

        # term returns 200+ literature
        data["search_string"] = (
            """(monomethyl OR MEP OR mono-n-butyl OR MBP OR mono (3-carboxypropyl) OR mcpp OR monobenzyl OR mbzp OR mono-isobutyl OR mibp OR mono (2-ethylhexyl) OR mono (2-ethyl-5-oxohexyl) OR meoph OR mono (2-ethyl-5-carboxypentyl) OR mecpp OR mepp OR mono (2-ethyl-5-hydroxyhexyl) OR mehp OR mono (2-ethyl-5-oxyhexyl) OR mono (2-ethyl-4-hydroxyhexyl) OR mono (2-ethyl-4-oxyhexyl) OR mono (2-carboxymethyl) OR mmhp OR mehp OR dehp OR 2-ethylhexanol OR (phthalic acid)) AND (liver OR hepato* OR hepat*) AND ((cell proliferation) OR (cell growth) OR (dna replication) OR (dna synthesis) OR (replicative dna synthesis) OR mitosis OR (cell division) OR (growth response) OR hyperplasia OR hepatomegaly) AND (mouse OR rat OR hamster OR rodent OR murine OR Mus musculus or Rattus)"""
        )

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
        n_new_pm_ids = pm_ids_qs.count()
        added_pmids = n_new_pm_ids - n_pm_ids
        assert added_pmids > 200
        assert models.Reference.objects.count() == added_pmids + initial_refs

        # check that some DOIs were added as well
        assert doi_ids_qs.count() - n_doi_ids_qs > 40

        # make sure a reference was created for each added PMID
        assert search.references.count() == added_pmids

    def test_import(self, db_keys):
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

        pmid_qs = models.Identifiers.objects.filter(database=constants.ReferenceDatabase.PUBMED)
        initial_pubmed_ids = pmid_qs.count()
        doi_qs = models.Identifiers.objects.filter(database=constants.ReferenceDatabase.DOI)
        initial_doi_ids = doi_qs.count()

        data["search_string"] = (
            "10357793, 20358181, 6355494, 8998951, 3383337, 12209194, 6677511, 11995694, 1632818, 12215663, 3180084, 14727734, 23625783, 11246142, 10485824, 3709451, 2877511, 6143560, 3934796, 8761421"
        )

        # check successful post
        url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
        response = client.post(url, data)
        assert response.status_code in [200, 302]

        # check new counts
        assert models.Search.objects.count() == initial_searches + 1
        assert models.Reference.objects.count() == initial_refs + 20

        # check both PMID and DOI were added
        assert pmid_qs.count() == initial_pubmed_ids + 20
        assert doi_qs.count() == initial_doi_ids + 2

        # make sure all each reference has an identifier
        i_pks = models.Identifiers.objects.values_list("pk", flat=True)
        assert i_pks.count() == initial_identifiers + 22
        assert (
            models.Reference.objects.filter(identifiers__in=i_pks).count()
            == initial_identifiers + 23
        )


@pytest.mark.vcr
@pytest.mark.django_db
class TestHero:
    def test_successful_single(self, db_keys):
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
            "search_string": "9961932",
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
        assert models.Identifiers.objects.count() == initial_identifiers + 3
        assert models.Reference.objects.count() == initial_refs + 1

        search = models.Search.objects.get(assessment=assessment_pk, title="example search")
        ref = models.Reference.objects.get(
            title="Occurrence of selected per- and polyfluorinated alkyl substances (PFASs) in food available on the European market - A review on levels and human exposure assessment"
        )
        assert models.Identifiers.objects.get(
            unique_id="9961932", database=constants.ReferenceDatabase.HERO
        )
        assert models.Identifiers.objects.get(
            unique_id="10.1016/j.chemosphere.2021.132378", database=constants.ReferenceDatabase.DOI
        )
        assert models.Identifiers.objects.get(
            unique_id="34592212", database=constants.ReferenceDatabase.PUBMED
        )

        assert ref.searches.all()[0] == search

    def test_failed(self, db_keys):
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
        data["search_string"] = "987654321"
        url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
        response = client.post(url, data)

        assertFormError(
            response.context["form"],
            "search_string",
            "The following HERO ID(s) could not be imported: 987654321",
        )
        assert models.Search.objects.count() == initial_searches

    def test_existing_pubmed(self, db_keys):
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

        doi_qs = models.Identifiers.objects.filter(unique_id="10.1016/s1011-1344(98)00183-3")
        assert doi_qs.exists() is False

        # build PubMed
        url = reverse("lit:search_new", kwargs={"pk": assessment_pk})
        response = client.post(url, pm_data)
        assert response.status_code in [200, 302]

        # Run PubMed Query
        url_run_query = reverse(
            "lit:search_query",
            kwargs={"pk": assessment_pk, "slug": pm_data["slug"]},
        )
        response = client.get(url_run_query)
        assert response.status_code in [200, 302]

        # assert that one object was created
        assert models.Search.objects.count() == initial_searches + 1
        assert models.Identifiers.objects.count() == initial_identifiers + 1
        assert models.Reference.objects.count() == initial_refs + 1
        assert doi_qs.exists() is False  # DOI not created by Pubmed

        # build HERO
        data["search_string"] = "1200"
        url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
        response = client.post(url, data)
        assert response.status_code in [200, 302]

        # assert that search & identifier created but not new reference
        assert models.Search.objects.count() == initial_searches + 2
        assert models.Identifiers.objects.count() == initial_identifiers + 3
        assert models.Reference.objects.count() == initial_refs + 1

        ref = models.Reference.objects.get(authors_short="Longstreth J et al.")
        assert ref.searches.count() == 2
        assert ref.identifiers.count() == 3
        assert doi_qs.exists() is True  # DOI created by HERO

    def test_hero_error(self, db_keys):
        """
        Test that a request that causes a HERO 500 error fails gracefully. Confirm:
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
            "search_string": "3856490, 3856492, 3856505, 3856507, 3856523",
        }

        # get initial counts
        initial_searches = models.Search.objects.count()

        # list of ids that causes an error
        url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
        response = client.post(url, data)

        assertFormError(
            response.context["form"],
            "search_string",
            "The following HERO ID(s) could not be imported: 3856490",
        )
        assert models.Search.objects.count() == initial_searches


class RisFile:
    def __init__(self, fn):
        self.path = fn


@pytest.mark.vcr
@pytest.mark.django_db
class TestRis:
    def test_ris_import(self, db_keys):
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
            in ris_ref.identifiers.filter(database=constants.ReferenceDatabase.PUBMED)
            .first()
            .content
        )

    def test_ris_import_with_existing(self, db_keys):
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
            database=constants.ReferenceDatabase.DOI,
            unique_id="10.1016/j.fct.2009.02.003",
            content="",
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

    def test_ris_with_doi(self, db_keys):
        """Check that additional DOI values are added from an RIS import"""

        # setup
        assessment_id = db_keys.assessment_working
        search = models.Search.objects.create(
            assessment_id=assessment_id,
            search_type="i",
            source=constants.ReferenceDatabase.RIS,
            title="ris-doi",
            slug="ris-doi",
            description="-",
        )
        search.import_file = RisFile(os.path.join(os.path.dirname(__file__), "data/with-doi.ris"))

        ref_qs = models.Reference.objects
        doi_qs = models.Identifiers.objects.filter(database=constants.ReferenceDatabase.DOI)

        n_ref_qs = ref_qs.count()
        n_dois = doi_qs.count()

        search.run_new_import()

        assert ref_qs.count() == n_ref_qs + 3
        assert doi_qs.count() == n_dois + 2

        # check that these exist and are properly associated with a reference
        assert models.Identifiers.objects.get(unique_id="10.1016/b36c36").references.count() == 1
        assert models.Identifiers.objects.get(unique_id="10.1016/b37c37").references.count() == 1
