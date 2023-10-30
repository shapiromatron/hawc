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

        data[
            "search_string"
        ] = "10357793, 20358181, 6355494, 8998951, 3383337, 12209194, 6677511, 11995694, 1632818, 12215663, 3180084, 14727734, 23625783, 11246142, 10485824, 3709451, 2877511, 6143560, 3934796, 8761421"

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
        data["search_string"] = "9876543321"
        url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
        response = client.post(url, data)

        assertFormError(
            response.context["form"],
            "search_string",
            "The following HERO ID(s) could not be imported: 9876543321",
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
            "search_string": "1200",
        }

        # get initial counts
        initial_searches = models.Search.objects.count()

        # list of ids that causes a 500 error
        ids = """2258, 30021, 88824, 128527, 198783, 346845, 488418, 509832, 625713, 670731, 688914, 716635, 732120, 752972, 782883, 819771, 1038270, 1039278, 1041030, 1043130, 1047045, 1047977, 1050876, 1055535, 1228147, 1230132, 1239433, 1249755, 1256375, 1274132, 1274137, 1274154, 1274159, 1274388, 1274396, 1274397, 1274410, 1274414, 1276109, 1276134, 1276159, 1279036, 1279037, 1279110, 1279127, 1289776, 1289780, 1289787, 1289788, 1289834, 1289837, 1289993, 1289999, 1290574, 1290806, 1290844, 1290868, 1290870, 1290887, 1290888, 1290891, 1290897, 1290898, 1291094, 1326734, 1332749, 1333757, 1401396, 1401660, 1404761, 1415983, 1424947, 1424948, 1424952, 1429952, 1445216, 1447841, 1450669, 1578499, 1578505, 1578507, 1578509, 1578517, 1597652, 1617974, 1618026, 1749076, 1849786, 1850369, 1937230, 2010072, 2010648, 2012721, 2022408, 2023785, 2029288, 2155195, 2170118, 2188967, 2190035, 2324788, 2324790, 2324807, 2324841, 2324895, 2324905, 2324911, 2325315, 2325320, 2325325, 2325327, 2325331, 2325333, 2325338, 2325339, 2325340, 2325346, 2325349, 2325356, 2325359, 2325374, 2325387, 2325421, 2325430, 2325435, 2325440, 2325492, 2347406, 2535067, 2535697, 2538743, 2538777, 2539072, 2549400, 2549482, 2553581, 2554838, 2558158, 2559310, 2559480, 2571454, 2573918, 2576635, 2583958, 2596083, 2621188, 2649641, 2668947, 2676749, 2718645, 2732071, 2816710, 2821611, 2823545, 2850027, 2850037, 2850041, 2850046, 2850049, 2850052, 2850058, 2850060, 2850063, 2850065, 2850068, 2850075, 2850078, 2850081, 2850087, 2850093, 2850096, 2850098, 2850106, 2850155, 2850159, 2850161, 2850168, 2850176, 2850183, 2850190, 2850202, 2850206, 2850221, 2850228, 2850246, 2850290, 2850294, 2850295, 2850306, 2850314, 2850316, 2850325, 2850369, 2850375, 2850380, 2850396, 2850404, 2850415, 2850416, 2850417, 2850900, 2850908, 2850910, 2850917, 2850944, 2850986, 2850995, 2851003, 2851005, 2851087, 2851149, 2851186, 2851198, 2851242, 2851285, 2912596, 2919147, 2919159, 2919200, 2919224, 2919238, 2919254, 2919262, 2919268, 2919269, 2919284, 2919288, 2919328, 2919380, 2946930, 2967086, 2970367, 2990271, 2991004, 3005562, 3005567, 3005573, 3008937, 3021018, 3021365, 3044613, 3076786, 3111116, 3114808, 3222653, 3223669, 3350475, 3351439, 3351873, 3351917, 3358129, 3359940, 3359967, 3360105, 3399236, 3448334, 3459209, 3468563, 3503518, 3604013, 3748720, 3748953, 3748959, 3749193, 3749284, 3749289, 3789699, 3790742, 3797537, 3810188, 3839729, 3841196, 3847344, 3856451, 3856453, 3856455, 3856456, 3856460, 3856464, 3856468, 3856470, 3856472, 3856480, 3856484, 3856486, 3856490, 3856492, 3856505, 3856507, 3856523, 3856549, 3856591, 3856639, 3856656, 3856668, 3856677, 3856851, 3856871, 3857361, 3857377, 3857382, 3857383, 3857384, 3857387, 3857400, 3857402, 3857454, 3858250, 3858259, 3858262, 3858263, 3858264, 3858272, 3858375, 3858444, 3858472, 3858477, 3858487, 3858488, 3858492, 3858500, 3858509, 3858510, 3858524, 3858541, 3858560, 3858607, 3858609, 3858617, 3858622, 3858637, 3858640, 3858645, 3858646, 3858650, 3858652, 3858670, 3858793, 3858797, 3858862, 3858922, 3858988, 3858989, 3859012, 3859243, 3859244, 3859253, 3859277, 3859278, 3859279, 3859281, 3859509, 3859523, 3859541, 3859602, 3859603, 3859606, 3859614, 3859625, 3859699, 3859700, 3859702, 3859703, 3859704, 3859705, 3859714, 3859719, 3859724, 3859737, 3859749, 3859757, 3859776, 3859786, 3859787, 3859788, 3859789, 3859790, 3859791, 3859792, 3859793, 3859794, 3859795, 3859797, 3859803, 3859805, 3859815, 3859817, 3859825, 3859833, 3859846, 3859849, 3859851, 3859873, 3859876, 3859910, 3859918, 3859919, 3859920, 3859921, 3859922, 3859924, 3859925, 3859926, 3859929, 3859930, 3859942, 3860099, 3860121, 3860206, 3860415, 3860584, 3860585, 3861414, 3861561, 3869265, 3878517, 3878944, 3898087, 3899858, 3899913, 3899973, 3921144, 3980872, 3980882, 3980883, 3980884, 3981209, 3981313, 3981322, 3981327, 3981347, 3981365, 3981417, 3981436, 3981451, 3981542, 3981549, 3981579, 3981721, 3981744, 3981789, 3981793, 3981929, 3981942, 3982004, 4111730, 4167113, 4174662, 4198322, 4220306, 4220307, 4220309, 4220319, 4220321, 4234856, 4234858, 4238291, 4238307, 4238322, 4238334, 4238377, 4238457, 4238497, 4238579, 4239163, 4241049, 4241051, 4241055, 4309149, 4309651, 4319287, 4348675, 4354081, 4354192, 4409296, 4510700, 4616440, 4618390, 4771044, 4774679, 4825616, 4940398, 4956575, 5017765, 5017777, 5024209, 5024210, 5024211, 5024294, 5063958, 5079687, 5079692, 5079753, 5079766, 5079787, 5079797, 5079799, 5079809, 5079816, 5079822, 5079846, 5079856, 5079967, 5079968, 5079969, 5079975, 5079986, 5080217, 5080229, 5080284, 5080298, 5080307, 5080312, 5080377, 5080385, 5080507, 5080513, 5080558, 5080583, 5080586, 5080589, 5080590, 5080618, 5080622, 5080628, 5080637, 5080638, 5080639, 5080643, 5080645, 5080663, 5081256, 5081271, 5081294, 5081333, 5081455, 5081488, 5082157, 5082215, 5083518, 5083552, 5083612, 5083667, 5083675, 5083689, 5084712, 5097904, 5097905, 5097906, 5097907, 5097908, 5097916, 5098313, 5098323, 5098324, 5098325, 5185472, 5352400, 5353624, 5381284, 5381304, 5381526, 5381531, 5381538, 5381555, 5381561, 5381565, 5381601, 5385935, 5385936, 5385937, 5386116, 5386987, 5386988, 5387106, 5387135, 5387136, 5387149, 5387157, 5387180, 5400977, 5412420, 5412466, 5412587, 5412596, 5413179, 5772415, 5880781, 5881135, 5883631, 5915992, 5916078, 5918597, 5918615, 5918616, 5918630, 5918764, 5918810, 5919109, 5935216, 6303224, 6303225, 6303226, 6303228, 6303229, 6304523, 6305866, 6311630, 6311631, 6311635, 6311681, 6315677, 6315680, 6315689, 6315690, 6315696, 6315698, 6315705, 6315734, 6315737, 6315771, 6315783, 6315785, 6315791, 6315808, 6315809, 6315810, 6316202, 6316209, 6316913, 6316920, 6318636, 6318642, 6318674, 6318676, 6322291, 6323799, 6323801, 6324256, 6324311, 6324329, 6324336, 6324898, 6326557, 6326943, 6326944, 6326945, 6326952, 6333653, 6333654, 6336059, 6336839, 6355453, 6356370, 6356901, 6356902, 6356904, 6360927, 6364788, 6364834, 6365007, 6387183, 6391241, 6391242, 6391291, 6392503, 6392504, 6392505, 6392507, 6416396, 6416397, 6505874, 6512132, 6512144, 6547066, 6553496, 6570001, 6574143, 6579272, 6703908, 6781357, 6822780, 6822781, 6822782, 6822783, 6827320, 6833596, 6833603, 6833604, 6833613, 6833658, 6833681, 6833688, 6833693, 6833694, 6833697, 6833705, 6833708, 6833715, 6833739, 6833741, 6833762, 6835448, 6835451, 6835499, 6835515, 6836806, 6956652, 6970864, 6985026, 6986805, 6987659, 6987891, 6988489, 6988495, 6988500, 6988503, 6988504, 6988506, 6988530, 6988531, 6994610, 7002817, 7014910, 7014912, 7019132, 7019179, 7019180, 7019181, 7019253, 7019434, 7021512, 7021776, 7023161, 7026347, 7065615, 7065644, 7127728, 7161477, 7174629, 7270234, 7276919, 7277659, 7277661, 7277663, 7277677, 7287202, 7325713, 7325714, 7325715, 7325716, 7326015, 7328343, 7348867, 7383292, 7404066, 7404106, 7404111, 7404231, 7404232, 7404233, 7404234, 7404235, 7404236, 7410142, 7410143, 7410151, 7410159, 7410160, 7410161, 7410162, 7410195, 7484012, 7484013, 7484014, 7484296, 7484843, 7484844, 7484845, 7486056, 7486061, 7486084, 7486109, 7486119, 7486130, 7486699, 7486755, 7486826, 7487863, 7487886, 7487901, 7488541, 7489260, 7489270, 7490043, 7491230, 7491238, 7491240, 7491241, 7491242, 7491243, 7491244, 7491245, 7491246, 7491247, 7491248, 7491249, 7491251, 7491252, 7491253, 7491254, 7491255, 7491256, 7491258, 7491259, 8347180, 8438370, 8442183, 8442206, 8453078, 8630776, 9641336, 9642134, 9795126, 9944338, 9944351, 9944367, 9944377, 9956482, 9959466, 9959518, 9959521, 9959527, 9959533, 9959553, 9959556, 9959571, 9959598, 9959616, 9959621, 9959652, 9959664, 9959693, 9959770, 9960165, 9960166, 9960167, 9960168, 9960177, 9960179, 9960658, 9961931, 9961974, 9961991, 9961992, 9961993, 9961994, 9961995, 9962001, 9962212, 10004031, 10173768, 10176392, 10176410, 10176443, 10176444, 10176458, 10176467, 10176548, 10176584, 10176665, 10176686, 10176720, 10176742, 10176795, 10228134, 10273292, 10273305, 10273351, 10273354, 10273383, 10273384, 10273403, 10273404, 10273405, 10273406, 10273407, 10273408, 10273409, 10273410, 10273411, 10273412, 10284379, 10284765, 10328201, 10328914, 10328915, 10365981, 10366205, 10476114"""
        data["search_string"] = ids
        url = reverse("lit:import_new", kwargs={"pk": assessment_pk})
        response = client.post(url, data)

        assertFormError(
            response.context["form"],
            "search_string",
            f"The following HERO ID(s) could not be imported: {ids}",
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
