import os

import pytest

from hawc.services.nih import pubmed

PUBMED_API_KEY = os.environ.get("PUBMED_API_KEY")


@pytest.fixture(scope="class")
def pubmed_connect():
    pubmed.settings.connect(PUBMED_API_KEY)


@pytest.mark.skipif(
    PUBMED_API_KEY is None, reason="Test environment requires $PUBMED_API_KEY to be set."
)
@pytest.mark.vcr
@pytest.mark.usefixtures("pubmed_connect")
class TestPubMedSearch:
    def test_standard_query(self):
        term = "science[journal] AND breast cancer AND 2008[pdat]"
        search = pubmed.PubMedSearch(term=term)
        search.get_ids_count()
        search.get_ids()
        assert search.request_count == 1
        self._results_check(search)

    def test_multiquery(self):
        term = "science[journal] AND breast cancer AND 2008[pdat]"
        search = pubmed.PubMedSearch(term=term, retmax=3)
        search.get_ids_count()
        search.get_ids()
        assert search.request_count == 2
        self._results_check(search)

    def test_changes_from_previous_search(self):
        term = "science[journal] AND breast cancer AND 2008[pdat]"
        search = pubmed.PubMedSearch(term=term)
        search.get_ids_count()
        search.get_ids()
        old_ids_list = [999999, 19008416, 18927361, 18787170, 18487186]
        changes = search.get_changes_from_previous_search(old_ids_list=old_ids_list)
        assert changes["added"] == set([18239126, 18239125])
        assert changes["removed"] == set([999999])

    def test_complex_query(self):
        """Ensure complicated search term executes and returns results."""
        term = """(monomethyl OR MEP OR mono-n-butyl OR MBP OR mono (3-carboxypropyl) OR mcpp OR monobenzyl OR mbzp OR mono-isobutyl OR mibp OR mono (2-ethylhexyl) OR mono (2-ethyl-5-oxohexyl) OR meoph OR mono (2-ethyl-5-carboxypentyl) OR mecpp OR mepp OR mono (2-ethyl-5-hydroxyhexyl) OR mehp OR mono (2-ethyl-5-oxyhexyl) OR mono (2-ethyl-4-hydroxyhexyl) OR mono (2-ethyl-4-oxyhexyl) OR mono (2-carboxymethyl) OR mmhp OR mehp OR dehp OR 2-ethylhexanol OR (phthalic acid)) AND (liver OR hepato* OR hepat*) AND ((cell proliferation) OR (cell growth) OR (dna replication) OR (dna synthesis) OR (replicative dna synthesis) OR mitosis OR (cell division) OR (growth response) OR hyperplasia OR hepatomegaly) AND (mouse OR rat OR hamster OR rodent OR murine OR Mus musculus or Rattus)"""
        search = pubmed.PubMedSearch(term=term)
        search.get_ids_count()
        search.get_ids()
        assert len(search.ids) >= 212

    def test_fake(self, settings):
        settings.HAWC_FEATURES.FAKE_IMPORTS = True
        search = pubmed.PubMedSearch(term="foo")
        search.get_ids_count()
        search.get_ids()
        assert len(search.ids) == 1
        settings.HAWC_FEATURES.FAKE_IMPORTS = False

    def _results_check(self, search):
        assert search.id_count == 6
        results_list = [19008416, 18927361, 18787170, 18487186, 18239126, 18239125]
        assert search.ids == results_list


@pytest.mark.skipif(
    PUBMED_API_KEY is None, reason="Test environment requires $PUBMED_API_KEY to be set."
)
@pytest.mark.vcr
@pytest.mark.usefixtures("pubmed_connect")
class TestPubMedFetch:
    def test_standard_query(self):
        ids = [19008416, 18927361, 18787170, 18487186, 18239126, 18239125]
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        assert fetch.request_count == 1
        self._results_check(fetch, ids)

    def test_multiquery(self):
        ids = [19008416, 18927361, 18787170, 18487186, 18239126, 18239125]
        fetch = pubmed.PubMedFetch(id_list=ids, retmax=3)
        fetch.get_content()
        assert fetch.request_count == 2
        self._results_check(fetch, ids)

    def test_utf8(self):
        # these ids have UTF-8 text in the abstract; make sure we can import
        # and the abstract field captures this value.
        ids = [23878845, 16080930]
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        # assert that a unicode value exists in text
        assert fetch.content[0]["abstract"].find("\u03b1") > -1

    def test_collective_author(self):
        # this doesn't have an individual author but rather a collective author
        ids = [21860499]
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        assert fetch.content[0]["authors_short"] == "National Toxicology Program"

    def test_structured_abstract(self):
        """
        Ensured structured abstract XML is captured.

        Example: https://www.ncbi.nlm.nih.gov/pubmed/21813367/
        """
        ids = (21813367,)
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        abstract_text = """<span class="abstract_label">BACKGROUND: </span>People living or working in eastern Ohio and western West Virginia have been exposed to perfluorooctanoic acid (PFOA) released by DuPont Washington Works facilities.<br><span class="abstract_label">OBJECTIVES: </span>Our objective was to estimate historical PFOA exposures and serum concentrations experienced by 45,276 non-occupationally exposed participants in the C8 Health Project who consented to share their residential histories and a 2005-2006 serum PFOA measurement.<br><span class="abstract_label">METHODS: </span>We estimated annual PFOA exposure rates for each individual based on predicted calibrated water concentrations and predicted air concentrations using an environmental fate and transport model, individual residential histories, and maps of public water supply networks. We coupled individual exposure estimates with a one-compartment absorption, distribution, metabolism, and excretion (ADME) model to estimate time-dependent serum concentrations.<br><span class="abstract_label">RESULTS: </span>For all participants (n = 45,276), predicted and observed median serum concentrations in 2005-2006 are 14.2 and 24.3 ppb, respectively [Spearman's rank correlation coefficient (r(s)) = 0.67]. For participants who provided daily public well water consumption rate and who had the same residence and workplace in one of six municipal water districts for 5 years before the serum sample (n = 1,074), predicted and observed median serum concentrations in 2005-2006 are 32.2 and 40.0 ppb, respectively (r(s) = 0.82).<br><span class="abstract_label">CONCLUSIONS: </span>Serum PFOA concentrations predicted by linked exposure and ADME models correlated well with observed 2005-2006 human serum concentrations for C8 Health Project participants. These individualized retrospective exposure and serum estimates are being used in a variety of epidemiologic studies being conducted in this region."""
        assert fetch.content[0]["abstract"] == abstract_text

    def test_abstract_with_child_text(self):
        """
        Ensure abstracts w/ html spans like <i></i> can be captured.

        Example: https://www.ncbi.nlm.nih.gov/pubmed/29186030
        """
        ids = (29186030,)
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        abstract_text = """CYP353D1v2 is a cytochrome P450 related to imidacloprid resistance in Laodelphax striatellus. This work was conducted to examine the ability of CYP353D1v2 to metabolize other insecticides. Carbon monoxide difference spectra analysis indicates that CYP353D1v2 was successfully expressed in insect cell Sf9. The catalytic activity of CYP353D1v2 relating to degrading buprofezin, chlorpyrifos, and deltamethrin was tested by measuring substrate depletion and analyzing the formation of metabolites. The results showed the nicotinamide-adenine dinucleotide phosphate (NADPH)-dependent depletion of buprofezin (eluting at 8.7 min) and parallel formation of an unknown metabolite (eluting 9.5 min). However, CYP353D1v2 is unable to metabolize deltamethrin and chlorpyrifos. The recombinant CYP353D1v2 protein efficiently catalyzed the model substrate p-nitroanisole with a maximum velocity of 9.24 nmol/min/mg of protein and a Michaelis constant of Km = 6.21 µM. In addition, imidacloprid was metabolized in vitro by the recombinant CYP353D1v2 microsomes (catalytic constant Kcat) 0.064 pmol/min/pmol P450, Km = 6.41 µM. The mass spectrum of UPLC-MS analysis shows that the metabolite was a product of buprofezin, which was buprofezin sulfone. This result provided direct evidence that L. striatellus cytochrome P450 CYP353D1v2 is capable of metabolizing imidacloprid and buprofezin."""
        assert fetch.content[0]["abstract"] == abstract_text

    def test_title_with_child_text(self):
        ids = (27933116,)
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        title = "Phoenix dactylifera mediated green synthesis of Cu2O particles for arsenite uptake from water."
        assert fetch.content[0]["title"] == title

    def test_doi(self):
        """
        Ensure DOI is obtained.

        Ex: https://www.ncbi.nlm.nih.gov/pubmed/21813142?retmod=xml&report=xml&format=text  # NOQA
        """
        ids = (21813142,)
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        doi = "10.1016/j.medcli.2011.05.017"
        assert fetch.content[0]["doi"] == doi

    def test_book(self):
        ids = (26468569,)
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        obj = fetch.content[0]
        obj.pop("xml")
        obj.pop("abstract")
        expected = {
            "authors_short": "Committee on Predictive-Toxicology Approaches for Military Assessments of Acute Exposures et al.",
            "doi": "10.17226/21775",
            "year": 2015,
            "PMID": 26468569,
            "title": "Application of Modern Toxicology Approaches for Predicting Acute Toxicity for Chemical Defense",
            "citation": "(2015). Washington (DC): National Academies Press (US).",
            "authors": [
                "Committee on Predictive-Toxicology Approaches for Military Assessments of Acute Exposures",
                "Committee on Toxicology",
                "Board on Environmental Studies and Toxicology",
                "Board on Life Sciences",
                "Division on Earth and Life Studies",
                "The National Academies of Sciences, Engineering, and Medicine",
            ],
        }
        assert obj == expected

    def test_book_chapter(self):
        ids = (20301382,)
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        obj = fetch.content[0]
        obj.pop("xml")
        obj.pop("abstract")
        expected = {
            "PMID": 20301382,
            "authors": ["Goldstein A", "Falk MJ"],
            "authors_short": "Goldstein A and Falk MJ",
            "citation": "GeneReviews® (1993). Seattle (WA): University of Washington, Seattle.",
            "doi": None,
            "title": "Mitochondrial DNA Deletion Syndromes",
            "year": 1993,
        }
        assert obj == expected

    def test_fake(self, settings):
        settings.HAWC_FEATURES.FAKE_IMPORTS = True
        ids = [12345, 123456]
        fetch = pubmed.PubMedFetch(id_list=ids)
        fetch.get_content()
        assert len(fetch.content) == 2
        actual_ids = [f["PMID"] for f in fetch.content]
        assert ids == actual_ids
        settings.HAWC_FEATURES.FAKE_IMPORTS = False

    def _results_check(self, fetch, ids):
        assert len(fetch.content) == 6
        assert [item["PMID"] for item in fetch.content] == ids

        # check journal citation
        expected = [
            "Science 2008; 322 (5908):1695-9",
            "Science 2008; 322 (5900):357",
            "Science 2008; 321 (5895):1499-502",
            "Science 2008; 320 (5878):903-9",
            "Science 2008; 319 (5863):620-4",
            "Science 2008; 319 (5863):617-20",
        ]
        actual = [item["citation"] for item in fetch.content]
        assert expected == actual

        # check short authors
        expected = [
            "Varambally S et al.",
            "Couzin J",
            "Mao JH et al.",
            "Bromberg KD et al.",
            "Schlabach MR et al.",
            "Silva JM et al.",
        ]
        actual = [item["authors_short"] for item in fetch.content]
        assert expected == actual
