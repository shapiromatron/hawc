import os

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from assessment.tests.utils import build_assessments_for_permissions_testing

from lit import constants, models


class ImportFormTest(TestCase):

    def setUp(self):
        build_assessments_for_permissions_testing(self)
        self.assessment_pk = self.assessment_working.pk
        self.client = Client()
        self.assertTrue(self.client.login(username='pm@pm.com', password='pw'))
        self.data = {
            'source': 2,
            'title': 'example search',
            'slug': 'example-search',
            'description': 'search description',
            'search_string': '1234, 1235, 12345'
        }

    def test_clean_import_string(self):

        # comma-separating checks
        failed_strings = [
            'string',
            '123, number, 1234',
            '-123',
            '123,,1234',
            '123, , 1234'
        ]
        for search_string in failed_strings:
            self.data['search_string'] = search_string
            response = self.client.post(
                reverse('lit:import_new', kwargs={"pk": self.assessment_pk}),
                self.data)
            self.assertFormError(
                response, 'form', 'search_string',
                'Please enter a comma-separated list of numeric IDs.')

        # ID uniqueness-check
        self.data['search_string'] = '123, 123'
        response = self.client.post(
            reverse('lit:import_new', kwargs={"pk": self.assessment_pk}),
            self.data)
        self.assertFormError(
            response, 'form', 'search_string', 'IDs must be unique.')


class PubMedTest(TestCase):

    def setUp(self):
        build_assessments_for_permissions_testing(self)
        self.assessment_pk = self.assessment_working.pk
        self.client = Client()
        self.assertTrue(self.client.login(username='pm@pm.com', password='pw'))
        self.data = {
            'source': 1,  # PubMed
            'title': 'pm search',
            'slug': 'pm-search',
            'description': 'search description',
            'search_string': '1998 Longstreth health risks ozone depletion'
        }

    def test_search(self):
        # Check when searching, the same number of identifiers and refs are
        # created, with refs fully-qualified with identifiers and searches

        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 2)  # manual imports
        self.assertEqual(models.Identifiers.objects.count(), 0)

        # term returns 200+ literature
        self.data['search_string'] = """(monomethyl OR MEP OR mono-n-butyl OR MBP OR mono (3-carboxypropyl) OR mcpp OR monobenzyl OR mbzp OR mono-isobutyl OR mibp OR mono (2-ethylhexyl) OR mono (2-ethyl-5-oxohexyl) OR meoph OR mono (2-ethyl-5-carboxypentyl) OR mecpp OR mepp OR mono (2-ethyl-5-hydroxyhexyl) OR mehp OR mono (2-ethyl-5-oxyhexyl) OR mono (2-ethyl-4-hydroxyhexyl) OR mono (2-ethyl-4-oxyhexyl) OR mono (2-carboxymethyl) OR mmhp OR mehp OR dehp OR 2-ethylhexanol OR (phthalic acid)) AND (liver OR hepato* OR hepat*) AND ((cell proliferation) OR (cell growth) OR (dna replication) OR (dna synthesis) OR (replicative dna synthesis) OR mitosis OR (cell division) OR (growth response) OR hyperplasia OR hepatomegaly) AND (mouse OR rat OR hamster OR rodent OR murine OR Mus musculus or Rattus)"""

        # check successful post
        url = reverse('lit:search_new', kwargs={"pk": self.assessment_pk})
        response = self.client.post(url, self.data)
        self.assertTrue(response.status_code in [200, 302])

        # run search
        search = models.Search.objects.latest()
        url = reverse('lit:search_query',
                      kwargs={"pk": self.assessment_pk, "slug": search.slug})
        response = self.client.get(url, self.data)
        self.assertTrue(response.status_code in [200, 302])

        self.assertEqual(models.Search.objects.count(), 3)
        i_count = models.Identifiers.objects.count()
        self.assertTrue(i_count > 200)
        self.assertEqual(models.Reference.objects.count(), i_count)

        # make sure all each reference has an identifier
        i_pks = models.Identifiers.objects.values_list('pk', flat=True)
        self.assertEqual(
            models.Reference.objects.filter(identifiers__in=i_pks).count(), i_count)

        # make sure all references associated with search
        self.assertEqual(models.Reference.objects.filter(searches=search).count(), i_count)

    def test_import(self):
        # ensure successful PubMed import

        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 2)  # manual imports
        self.assertEqual(models.Identifiers.objects.count(), 0)

        self.data['search_string'] = '10357793, 20358181, 6355494, 8998951, 3383337, 12209194, 6677511, 11995694, 1632818, 12215663, 3180084, 14727734, 23625783, 11246142, 10485824, 3709451, 2877511, 6143560, 3934796, 8761421'

        # check successful post
        url = reverse('lit:import_new', kwargs={"pk": self.assessment_pk})
        response = self.client.post(url, self.data)
        self.assertTrue(response.status_code in [200, 302])

        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 20)
        self.assertEqual(models.Search.objects.count(), 3)
        self.assertEqual(models.Identifiers.objects.count(), 20)

        # make sure all each reference has an identifier
        i_pks = models.Identifiers.objects.values_list('pk', flat=True)
        search = models.Search.objects.latest()
        self.assertEqual(i_pks.count(), 20)
        self.assertEqual(models.Reference.objects.filter(identifiers__in=i_pks).count(), 20)

        # make sure all references associated with search
        self.assertEqual(models.Reference.objects.filter(searches=search).count(), 20)


class HEROTest(TestCase):

    def setUp(self):
        build_assessments_for_permissions_testing(self)
        self.assessment_pk = self.assessment_working.pk
        self.client = Client()
        self.assertTrue(self.client.login(username='pm@pm.com', password='pw'))
        self.data = {
            'source': 2,  # HERO
            'title': 'example search',
            'slug': 'example-search',
            'description': 'search description',
            'search_string': '1200'
        }
        self.pm_data = {
            'source': 1,  # PubMed
            'title': 'pm search',
            'slug': 'pm-search',
            'description': 'search description',
            'search_string': '1998 Longstreth health risks ozone depletion'
        }

    def test_successful_single_hero_id(self):
        # Test that a single hero ID can be added. Confirm:
        # 1) Reference created
        # 2) Reference associated with search
        # 3) Reference associated with literature

        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 2)  # manual imports
        self.assertEqual(models.Identifiers.objects.count(), 0)

        # check successful post
        url = reverse('lit:import_new', kwargs={"pk": self.assessment_pk})
        response = self.client.post(url, self.data)
        self.assertTrue(response.status_code in [200, 302])

        # check expected results
        self.assertEqual(models.Search.objects.count(), 3)
        self.assertEqual(models.Identifiers.objects.count(), 1)
        self.assertEqual(models.Reference.objects.count(), 1)
        ref = models.Reference.objects.all()[0]

        search = models.Search.objects.get(assessment=self.assessment_pk, title='example search')
        ident = models.Identifiers.objects.all()[0]
        self.assertEqual(ref.searches.all()[0], search)
        self.assertEqual(ref.identifiers.all()[0], ident)

    def test_failed_hero_id(self):
        # Test that a hero ID that doesn't exist fails gracefully. Confirm:
        # 1) Search created
        # 2) No reference created, no literature

        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 2)  # manual imports
        self.assertEqual(models.Identifiers.objects.count(), 0)

        # known hero ID that doesn't exist
        self.data['search_string'] = '9999999'
        url = reverse('lit:import_new', kwargs={"pk": self.assessment_pk})
        response = self.client.post(url, self.data)

        # check completion as as expected
        self.assertTrue(response.status_code in [200, 302])
        self.assertEqual(models.Search.objects.count(), 3)
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Identifiers.objects.count(), 0)

    def test_existing_pubmed_hero_add(self):
        # Check that search is complete, new identifier is created, but is
        # associated with existing PubMed Reference

        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 2)  # manual imports
        self.assertEqual(models.Identifiers.objects.count(), 0)

        # build PubMed
        url = reverse('lit:search_new', kwargs={"pk": self.assessment_pk})
        response = self.client.post(url, self.pm_data)
        self.assertTrue(response.status_code in [200, 302])

        # Run PubMed Query
        url_run_query = reverse(
            'lit:search_query',
            kwargs={"pk": self.assessment_pk, "slug": self.pm_data['slug']})
        response = self.client.get(url_run_query)
        self.assertTrue(response.status_code in [200, 302])

        # assert that one object was created
        self.assertEqual(models.Reference.objects.count(), 1)
        self.assertEqual(models.Search.objects.count(), 3)
        self.assertEqual(models.Identifiers.objects.count(), 1)

        # build HERO
        self.data['search_string'] = '1200'
        url = reverse('lit:import_new', kwargs={"pk": self.assessment_pk})
        response = self.client.post(url, self.data)
        self.assertTrue(response.status_code in [200, 302])

        # assert that search & identifier created but not new reference
        self.assertEqual(models.Search.objects.count(), 4)
        self.assertEqual(models.Identifiers.objects.count(), 2)
        self.assertEqual(models.Reference.objects.count(), 1)

        ref = models.Reference.objects.all()[0]
        self.assertEqual(ref.searches.count(), 2)
        self.assertEqual(ref.identifiers.count(), 2)


class TestFile(object):
    def __init__(self, fn):
        self.path = fn


class RISImportTest(TestCase):

    def setUp(self):
        build_assessments_for_permissions_testing(self)
        self.search = models.Search.objects.create(
            assessment_id=self.assessment_working.pk,
            search_type="i",
            source=constants.RIS,
            title="ris",
            slug="ris",
            description="-",
        )
        self.search.import_file = TestFile(os.path.join(os.path.dirname(__file__), "data/single_ris.txt"))

    def test_import(self):
        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 3)
        self.assertEqual(models.Identifiers.objects.count(), 0)

        self.search.run_new_import()
        self.assertEqual(models.Reference.objects.count(), 1)
        self.assertEqual(models.Identifiers.objects.count(), 3)
        self.assertEqual(models.Reference.objects.first().identifiers.count(), 3)

        self.assertEqual(models.Identifiers.objects.filter(database=constants.PUBMED).count(), 1)
        self.assertEqual(models.Identifiers.objects.filter(database=constants.RIS).count(), 1)
        self.assertEqual(models.Identifiers.objects.filter(database=constants.DOI).count(), 1)

        # assert Pubmed XML content is loaded
        self.assertTrue(
            "<PubmedArticle>" in
            models.Identifiers.objects.filter(database=constants.PUBMED).first().content
        )

    def test_import_with_existing(self):
        # check initially blank
        self.assertEqual(models.Reference.objects.count(), 0)
        self.assertEqual(models.Search.objects.count(), 3)
        self.assertEqual(models.Identifiers.objects.count(), 0)

        # create existing identifiers
        models.Identifiers.objects.create(
            database=constants.PUBMED, unique_id="19425233", content="None")
        models.Identifiers.objects.create(
            database=constants.DOI, unique_id="10.1016/j.fct.2009.02.003", content="None")

        self.search.run_new_import()
        self.assertEqual(models.Reference.objects.count(), 1)
        self.assertEqual(models.Identifiers.objects.count(), 3)
        self.assertEqual(models.Reference.objects.first().identifiers.count(), 3)

        # ensure new ones aren't created
        self.assertEqual(models.Identifiers.objects.filter(database=constants.PUBMED).count(), 1)
        self.assertEqual(models.Identifiers.objects.filter(database=constants.RIS).count(), 1)
        self.assertEqual(models.Identifiers.objects.filter(database=constants.DOI).count(), 1)
