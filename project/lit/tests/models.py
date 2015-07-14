from django.test import TestCase

from lit.fetchers.pubmed import PubMedSearch, PubMedFetch
from lit.fetchers.hero import HEROFetch
from lit.fetchers.utils import get_author_short_text


class PubMedSearchTests(TestCase):
    """
    Make sure that a PubMed search with returns the expected number of IDS,
    and that all IDs are identical to what were expected. Example from the
    PubMed quickstart guide here:

        http://www.ncbi.nlm.nih.gov/books/NBK25500/

    """
    def setUp(self):
        self.term = "science[journal] AND breast cancer AND 2008[pdat]"
        self.results_list = [19008416, 18927361, 18787170, 18487186, 18239126, 18239125]

    def test_standard_query(self):
        self.search = PubMedSearch(term=self.term)
        self.search.get_ids_count()
        self.search.get_ids()
        self.assertEqual(self.search.request_count, 1)
        self._results_check()

    def test_multiquery(self):
        self.search = PubMedSearch(term=self.term, retmax=3)
        self.search.get_ids_count()
        self.search.get_ids()
        self.assertEqual(self.search.request_count, 2)
        self._results_check()

    def test_changes_from_previous_search(self):
        self.search = PubMedSearch(term=self.term)
        self.search.get_ids_count()
        self.search.get_ids()
        old_ids_list = [999999, 19008416, 18927361, 18787170, 18487186]
        changes = self.search.get_changes_from_previous_search(old_ids_list=old_ids_list)
        self.assertEqual(changes['added'], set([18239126, 18239125]))
        self.assertEqual(changes['removed'], set([999999]))

    def test_complex_query(self):
        """
        Make sure that we can send a very complicated search term
        and the results that at least some results are returned. This is
        commonly done when using MeSH search terms in PubMed.
        """
        self.term = """(monomethyl OR MEP OR mono-n-butyl OR MBP OR mono (3-carboxypropyl) OR mcpp OR monobenzyl OR mbzp OR mono-isobutyl OR mibp OR mono (2-ethylhexyl) OR mono (2-ethyl-5-oxohexyl) OR meoph OR mono (2-ethyl-5-carboxypentyl) OR mecpp OR mepp OR mono (2-ethyl-5-hydroxyhexyl) OR mehp OR mono (2-ethyl-5-oxyhexyl) OR mono (2-ethyl-4-hydroxyhexyl) OR mono (2-ethyl-4-oxyhexyl) OR mono (2-carboxymethyl) OR mmhp OR mehp OR dehp OR 2-ethylhexanol OR (phthalic acid)) AND (liver OR hepato* OR hepat*) AND ((cell proliferation) OR (cell growth) OR (dna replication) OR (dna synthesis) OR (replicative dna synthesis) OR mitosis OR (cell division) OR (growth response) OR hyperplasia OR hepatomegaly) AND (mouse OR rat OR hamster OR rodent OR murine OR Mus musculus or Rattus)"""
        self.search = PubMedSearch(term=self.term)
        self.search.get_ids_count()
        self.search.get_ids()
        self.assertTrue(self.search.ids >= 212)

    def _results_check(self):
        self.assertEqual(self.search.id_count, 6)
        self.assertListEqual(self.search.ids, self.results_list)


class PubMedFetchTests(TestCase):
    """
    Make sure that a PubMed search with returns the expected number of IDS,
    and that all IDs are identical to what were expected. Example from the
    PubMed quickstart guide here:

        http://www.ncbi.nlm.nih.gov/books/NBK25500/

    """
    def setUp(self):
        self.ids = [19008416, 18927361, 18787170, 18487186, 18239126, 18239125]

    def test_standard_query(self):
        self.fetch = PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        self.assertEqual(self.fetch.request_count, 1)
        self._results_check()

    def test_multiquery(self):
        self.fetch = PubMedFetch(id_list=self.ids, retmax=3)
        self.fetch.get_content()
        self.assertEqual(self.fetch.request_count, 2)
        self._results_check()

    def test_utf8(self):
        # these ids have UTF-8 text in the abstract; make sure we can import
        # and the abstract field captures this value.
        self.ids = [23878845, 16080930]
        self.fetch = PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        # assert that a unicode value exists in text
        self.assertTrue(self.fetch.content[0]['abstract'].find(u'\u03b1') > -1)

    def test_collective_author(self):
        # this doesn't have an individual author but rather a collective author
        self.ids = [21860499]
        self.fetch = PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        self.assertEqual(
            self.fetch.content[0]['authors_short'],
            u'National Toxicology Program'
        )

    def test_structured_abstract(self):
        """
        Some abstracts have structure in XML; make sure HAWC can import these.
        For example: http://www.ncbi.nlm.nih.gov/pubmed/21813367
        """
        self.ids = (21813367, )
        self.fetch = PubMedFetch(id_list=self.ids)
        self.fetch.get_content()
        abstract_text = u"""<span class='abstract_label'>BACKGROUND: </span>People living or working in eastern Ohio and western West Virginia have been exposed to perfluorooctanoic acid (PFOA) released by DuPont Washington Works facilities.<br><span class='abstract_label'>OBJECTIVES: </span>Our objective was to estimate historical PFOA exposures and serum concentrations experienced by 45,276 non-occupationally exposed participants in the C8 Health Project who consented to share their residential histories and a 2005-2006 serum PFOA measurement.<br><span class='abstract_label'>METHODS: </span>We estimated annual PFOA exposure rates for each individual based on predicted calibrated water concentrations and predicted air concentrations using an environmental fate and transport model, individual residential histories, and maps of public water supply networks. We coupled individual exposure estimates with a one-compartment absorption, distribution, metabolism, and excretion (ADME) model to estimate time-dependent serum concentrations.<br><span class='abstract_label'>RESULTS: </span>For all participants (n = 45,276), predicted and observed median serum concentrations in 2005-2006 are 14.2 and 24.3 ppb, respectively [Spearman's rank correlation coefficient (r(s)) = 0.67]. For participants who provided daily public well water consumption rate and who had the same residence and workplace in one of six municipal water districts for 5 years before the serum sample (n = 1,074), predicted and observed median serum concentrations in 2005-2006 are 32.2 and 40.0 ppb, respectively (r(s) = 0.82).<br><span class='abstract_label'>CONCLUSIONS: </span>Serum PFOA concentrations predicted by linked exposure and ADME models correlated well with observed 2005-2006 human serum concentrations for C8 Health Project participants. These individualized retrospective exposure and serum estimates are being used in a variety of epidemiologic studies being conducted in this region."""  # NOQA
        self.assertEqual(self.fetch.content[0]['abstract'], abstract_text)

    def _results_check(self):
        self.assertEqual(len(self.fetch.content), 6)
        self.assertListEqual(
            [item['PMID'] for item in self.fetch.content],
            self.ids
        )

        citations = [
            "Science 2008; 322 (5908):1695-9",
            "Science 2008; 322 (5900):357",
            "Science 2008; 321 (5895):1499-502",
            "Science 2008; 320 (5878):903-9",
            "Science 2008; 319 (5863):620-4",
            "Science 2008; 319 (5863):617-20"
        ]
        self.assertListEqual(
            [item['citation'] for item in self.fetch.content],
            citations
        )

        authors_short = [
            "Varambally S et al.",
            "Couzin J",
            "Mao JH et al.",
            "Bromberg KD et al.",
            "Schlabach MR et al.",
            "Silva JM et al."
        ]
        self.assertListEqual(
            [item['authors_short'] for item in self.fetch.content],
            authors_short
        )


class HEROFetchTests(TestCase):

    def test_success_query(self):
        # ensure that we get the correct query returned
        ids = (1201, )
        hero_getter = HEROFetch(id_list=ids)
        hero_getter.get_content()
        self.assertListEqual(hero_getter.failures, [])
        self.assertEqual(len(hero_getter.content), 1)

        val = hero_getter.content[0]

        # test individual components
        self.assertEqual(val['HEROID'], 1201)
        self.assertEqual(val['PMID'], 9922222)
        self.assertListEqual(val['authors_list'], [
            u'Farman CA', u'Watkins K', u'Van Hoozen B',
            u'Last JA', u'Witschi H', u'Pinkerton KE'
        ])
        self.assertEqual(val['authors_short'], u'Farman CA et al.')
        self.assertEqual(
            val['title'],
            u'Centriacinar remodeling and sustained procollagen gene expression after exposure to ozone and nitrogen dioxide')
        self.assertEqual(val['year'], 1999)
        self.assertEqual(
            val['abstract'],
            u'Sprague-Dawley rats were exposed to 0.8 ppm ozone (O3), to 14.4 ppm nitrogen dioxide (NO2), or to both gases simultaneously for 6 h per day for up to 90 d. The extent of histopathologic changes within the central acinus of the lungs was compared after 7 or 78 to 90 d of exposure using morphometric analysis by placement of concentric arcs radiating outward from a single reference point at the level of the bronchiole- alveolar duct junction. Lesions in the lungs of rats exposed to the mixture of gases extended approximately twice as far into the acinus as in those exposed to each individual gas. The extent of tissue involvement was the same at 78 to 90 d as noted at 7 d in all exposure groups. At the end of exposure, in situ hybridization for procollagen types I and III demonstrated high levels of messenger RNA within central acini in the lungs of animals exposed to the combination of O3 and NO2. In contrast, animals exposed to each individual gas had a similar pattern of message expression compared with that seen in control animals, although centriacinar histologic changes were still significantly different from control animals. We conclude that the progressive pulmonary fibrosis that occurs in rats exposed to the combination of O3 and NO2 is due to sustained, elevated expression of the genes for procollagen types I and III. This effect at the gene level is correlated with the more severe histologic lesions seen in animals exposed to both O3 and NO2 compared with those exposed to each individual gas. In contrast, the sustained expression of the procollagen genes is not associated with a shift in the distribution of the lesions because the area of change in each group after 7 d of exposure was the same as after 78 to 90 d of exposure.')
        # Note that we don't test the raw JSON as the score and literature search
        # may change; as long as we get out what we want, we should be ok.

    def test_bigger_query(self):
        # Ensure that we can get hundreds of results at once, and confirm that
        # we are properly getting processing content and failures
        ids = range(1200, 1405)
        hero_getter = HEROFetch(id_list=ids)
        hero_getter.get_content()
        self.assertEqual(len(hero_getter.content), 198)
        self.assertEqual(len(hero_getter.failures), 7)
        self.assertListEqual(
            hero_getter.failures,
            [1349, 1319, 1224, 1227, 1228, 1361, 1366])


class AuthorParsingTests(TestCase):

    def test_parsing(self):
        # 0 test
        self.assertEqual(
            u'',
            get_author_short_text([]))

        # 1 test
        self.assertEqual(
            u'Smith J',
            get_author_short_text(['Smith J']))

        # 2 test
        self.assertEqual(
            u'Smith J and Smith J',
            get_author_short_text(['Smith J']*2))

        # 3 test
        self.assertEqual(
            u'Smith J, Smith J, and Smith J',
            get_author_short_text(['Smith J']*3))

        # 4 test
        self.assertEqual(
            u'Smith J et al.',
            get_author_short_text(['Smith J']*4))
