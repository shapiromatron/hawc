import logging

import pytest
import requests
from django.conf import settings as django_settings

from hawc.services.epa import hero
from hawc.services.epa.hero import HEROFetch


@pytest.mark.parametrize(
    ("content", "expected"),
    [({"a": "null"}, None), ({"a": "value"}, "value"), ({}, None)],
)
def test_parse_pseudo_json(content, expected):
    assert hero._parse_pseudo_json(content, "a") == expected


class TestHEROFetch:
    @pytest.mark.vcr
    def test_hero_success_query(self):
        # ensure that we get the correct query returned
        hero_getter = HEROFetch(id_list=[1201])
        hero_getter.get_content()

        assert len(hero_getter.content) == 1
        assert len(hero_getter.failures) == 0

        val = hero_getter.content[0]
        assert val.pop("json") is not None
        assert val == {
            "HEROID": 1201,
            "PMID": 9922222,
            "doi": "10.1165/ajrcmb.20.2.3269",
            "title": "Centriacinar remodeling and sustained procollagen gene expression after exposure to ozone and nitrogen dioxide",
            "abstract": "Sprague-Dawley rats were exposed to 0.8 ppm ozone (O3), to 14.4 ppm nitrogen dioxide (NO2), or to both gases simultaneously for 6 h per day for up to 90 d. The extent of histopathologic changes within the central acinus of the lungs was compared after 7 or 78 to 90 d of exposure using morphometric analysis by placement of concentric arcs radiating outward from a single reference point at the level of the bronchiole- alveolar duct junction. Lesions in the lungs of rats exposed to the mixture of gases extended approximately twice as far into the acinus as in those exposed to each individual gas. The extent of tissue involvement was the same at 78 to 90 d as noted at 7 d in all exposure groups. At the end of exposure, in situ hybridization for procollagen types I and III demonstrated high levels of messenger RNA within central acini in the lungs of animals exposed to the combination of O3 and NO2. In contrast, animals exposed to each individual gas had a similar pattern of message expression compared with that seen in control animals, although centriacinar histologic changes were still significantly different from control animals. We conclude that the progressive pulmonary fibrosis that occurs in rats exposed to the combination of O3 and NO2 is due to sustained, elevated expression of the genes for procollagen types I and III. This effect at the gene level is correlated with the more severe histologic lesions seen in animals exposed to both O3 and NO2 compared with those exposed to each individual gas. In contrast, the sustained expression of the procollagen genes is not associated with a shift in the distribution of the lesions because the area of change in each group after 7 d of exposure was the same as after 78 to 90 d of exposure.",
            "source": "American Journal of Respiratory Cell and Molecular Biology 20:303-311.",
            "year": 1999,
            "authors": [
                "Farman CA",
                "Watkins K",
                "Van Hoozen B",
                "Last JA",
                "Witschi H",
                "Pinkerton KE",
            ],
            "authors_short": "Farman CA et al.",
        }

    @pytest.mark.vcr
    def test_new_hero_success(self, settings):
        settings.HAWC_FEATURES.ENABLE_NEW_HERO = True
        hero_getter = HEROFetch(id_list=[1201])
        hero_getter.get_content()

        assert len(hero_getter.content) == 1
        assert len(hero_getter.failures) == 0

        val = hero_getter.content[0]
        assert val.pop("json") is not None
        assert val == {
            "HEROID": 1201,
            "PMID": 9922222,
            "doi": "10.1165/ajrcmb.20.2.3269",
            "title": "Centriacinar remodeling and sustained procollagen gene expression after exposure to ozone and nitrogen dioxide",
            "abstract": "Sprague-Dawley rats were exposed to 0.8 ppm ozone (O3), to 14.4 ppm nitrogen dioxide (NO2), or to both gases simultaneously for 6 h per day for up to 90 d. The extent of histopathologic changes within the central acinus of the lungs was compared after 7 or 78 to 90 d of exposure using morphometric analysis by placement of concentric arcs radiating outward from a single reference point at the level of the bronchiole- alveolar duct junction. Lesions in the lungs of rats exposed to the mixture of gases extended approximately twice as far into the acinus as in those exposed to each individual gas. The extent of tissue involvement was the same at 78 to 90 d as noted at 7 d in all exposure groups. At the end of exposure, in situ hybridization for procollagen types I and III demonstrated high levels of messenger RNA within central acini in the lungs of animals exposed to the combination of O3 and NO2. In contrast, animals exposed to each individual gas had a similar pattern of message expression compared with that seen in control animals, although centriacinar histologic changes were still significantly different from control animals. We conclude that the progressive pulmonary fibrosis that occurs in rats exposed to the combination of O3 and NO2 is due to sustained, elevated expression of the genes for procollagen types I and III. This effect at the gene level is correlated with the more severe histologic lesions seen in animals exposed to both O3 and NO2 compared with those exposed to each individual gas. In contrast, the sustained expression of the procollagen genes is not associated with a shift in the distribution of the lesions because the area of change in each group after 7 d of exposure was the same as after 78 to 90 d of exposure.",
            "source": "Am J Respir Cell Mol Biol. 20:303-311",
            "year": 1999,
            "authors": [
                "Farman CA",
                "Watkins K",
                "Van Hoozen B",
                "Last JA",
                "Witschi H",
                "Pinkerton KE",
            ],
            "authors_short": "Farman CA et al.",
        }
        settings.HAWC_FEATURES.ENABLE_NEW_HERO = False

    @pytest.mark.vcr
    def test_hero_bigger_query(self):
        # Check that we can get hundreds of results at once; and ensure failures are captured.
        hero_getter = HEROFetch(id_list=list(range(50000, 50100)))
        hero_getter.get_content()

        assert len(hero_getter.content) == 98
        assert len(hero_getter.failures) == 2
        assert hero_getter.failures == [50017, 50058]

    @pytest.mark.vcr
    def test_pmid_parsing(self):
        # assert PMID is parsed correctly
        hero_getter = HEROFetch(id_list=list(range(50000, 50100)))
        hero_getter.get_content()

        assert hero_getter.content[0]["PMID"] == 12654040
        assert hero_getter.content[2]["PMID"] is None

    @pytest.mark.vcr
    def test_source_parsing(self, settings):
        # check custom parsing function for various references

        ids = [54501, 5708371]  # journal, ECHA dossier

        hero_getter = HEROFetch(id_list=ids)
        hero_getter.get_content()
        sources = [d["source"] for d in hero_getter.content]
        assert sources == ["", "Environmental Health Perspectives 28:251-260."]

        settings.HAWC_FEATURES.ENABLE_NEW_HERO = True
        hero_getter = HEROFetch(id_list=ids)
        hero_getter.get_content()
        sources = [d["source"] for d in hero_getter.content]
        assert sources == ["Environ Health Perspect. 28:251-260", ""]
        settings.HAWC_FEATURES.ENABLE_NEW_HERO = False

    def test_fake(self, settings):
        settings.HAWC_FEATURES.FAKE_IMPORTS = True
        ids = [123, 1234, 12345]
        fetch = HEROFetch(id_list=ids)
        fetch.get_content()
        assert [d["HEROID"] for d in fetch.content] == ids
        settings.HAWC_FEATURES.FAKE_IMPORTS = False

    def test_init_settings_override(self):
        assert HEROFetch(id_list=[1]).settings["recordsperpage"] == 100
        assert HEROFetch(id_list=[1], recordsperpage=5).settings["recordsperpage"] == 5

    def test_new_hero_missing_api_key(self, monkeypatch, settings):
        monkeypatch.setattr(django_settings.HAWC_FEATURES, "ENABLE_NEW_HERO", True)
        settings.HERO_API_KEY = None
        with pytest.raises(ValueError, match="HERO_API_KEY required"):
            HEROFetch(id_list=[1]).get_content()

    @pytest.mark.parametrize("new_hero", [False, True])
    @pytest.mark.parametrize(
        ("outcome", "message"),
        [
            ({"status_code": 500}, "HERO request failure"),
            (requests.exceptions.Timeout(), "HERO request timeout"),
            ({"text": "not json"}, "HERO request failure"),
        ],
    )
    def test_request_failures(
        self,
        monkeypatch,
        settings,
        caplog,
        build_response,
        build_session,
        new_hero,
        outcome,
        message,
    ):
        monkeypatch.setattr(django_settings.HAWC_FEATURES, "ENABLE_NEW_HERO", new_hero)
        settings.HERO_API_KEY = "key"
        if isinstance(outcome, dict):
            outcome = build_response(**outcome)
        session = build_session(outcome)
        monkeypatch.setattr(hero, "get_session", lambda headers=None: session)
        fetch = HEROFetch(id_list=[1, 2])
        caplog.set_level(logging.INFO, logger=hero.logger.name)
        result = fetch.get_content()
        assert result == {"success": [], "failure": [1, 2]}
        assert message in caplog.text
