import json
import logging
from typing import Any

import requests
from django.conf import settings

from hawc.services.utils.doi import try_get_doi

from ..utils.authors import get_author_short_text, normalize_authors

logger = logging.getLogger(__name__)


def _parse_pseudo_json(d: dict, field: str) -> Any:
    # built-in json parser doesn't identify nulls in HERO returns
    v = d.get(field, None)
    if v == "null":
        return None
    else:
        return v


def _force_int(val, default=None) -> int | None:
    try:
        return int(val)
    except Exception:
        return default


def parse_article(content: dict) -> dict:
    if settings.HAWC_FEATURES.ENABLE_NEW_HERO:
        authors = normalize_authors(content.get("authors", []))
        return dict(
            json=content,
            HEROID=_force_int(content.get("id")),
            PMID=_force_int(content.get("accession_number")),
            doi=try_get_doi(content.get("doi", "")),
            tilte=content.get("title"),
            abstract=content.get("abstract"),
            source=content.get("type_of_reference"),
            year=content.get("year"),
            authors=authors,
            authors_short=get_author_short_text(authors),
        )
    else:
        authors = normalize_authors(content.get("AUTHORS", "").split("; "))
        authors_short = get_author_short_text(authors)
        return dict(
            json=content,
            HEROID=_force_int(_parse_pseudo_json(content, "REFERENCE_ID")),
            PMID=_force_int(_parse_pseudo_json(content, "PMID")),
            doi=try_get_doi(_parse_pseudo_json(content, "doi")),
            title=_parse_pseudo_json(content, "TITLE"),
            abstract=_parse_pseudo_json(content, "ABSTRACT"),
            source=_parse_pseudo_json(content, "SOURCE"),
            year=_force_int(_parse_pseudo_json(content, "YEAR")),
            authors=authors,
            authors_short=authors_short,
        )


class HEROFetch:
    """
    Handler to search and retrieve literature from US EPA's HERO database.

    Given a list of HERO IDs, fetch the content for each one and return a
    list of dictionaries of citation information. Note that this citation
    includes the PubMed ID, if available in HERO.
    """

    default_settings = {"recordsperpage": 100}

    def __init__(self, id_list: list[int], **kwargs):
        if id_list is None:
            raise Exception("List of IDs are required for a PubMed search")
        self.ids = id_list
        self.ids_count = len(id_list)
        self.content: list[dict] = []
        self.failures: list[int] = []
        self.settings = HEROFetch.default_settings.copy()
        for k, v in kwargs.items():
            self.settings[k] = v

    def fake_content(self) -> list[dict]:
        return [
            {
                "json": {},
                "HEROID": id,
                "PMID": None,
                "doi": None,
                "title": "Reference Title",
                "abstract": "",
                "source": "123-456.",
                "year": 2023,
                "authors": ["Author 1", "Author 2"],
                "authors_short": "authors et al.",
            }
            for id in self.ids
        ]

    def get_content(self):
        if settings.HAWC_FEATURES.FAKE_IMPORTS:
            self.content = self.fake_content()
            self.failures = []
            return dict(success=self.content, failure=self.failures)

        rng = list(range(0, self.ids_count, self.settings["recordsperpage"]))
        for recstart in rng:
            request_ids = self.ids[recstart : recstart + self.settings["recordsperpage"]]
            ids = ",".join([str(id_) for id_ in request_ids])
            rpp = self.settings["recordsperpage"]
            results = []
            if settings.HAWC_FEATURES.ENABLE_NEW_HERO:
                url = "https://heronetnext.epa.gov/api/reference/export/json"
                params = {"id": request_ids, "type": "hero"}
                try:
                    r = requests.get(url, params, timeout=30.0)
                    if r.status_code == 200:
                        results = r.json()
                    else:
                        logger.info(f"HERO request failure: {url}")
                except requests.exceptions.Timeout:
                    logger.info(f"HERO request timeout: {url}")
                except json.JSONDecodeError:
                    logger.info(f"HERO request failure: {url}")
            else:
                url = f"https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/{ids}/recordsperpage/{rpp}.json"
                try:
                    r = requests.get(url, timeout=30.0)
                    if r.status_code == 200:
                        data = json.loads(r.text)
                        results = data["results"]
                    else:
                        logger.info(f"HERO request failure: {url}")
                except requests.exceptions.Timeout:
                    logger.info(f"HERO request timeout: {url}")
                except json.JSONDecodeError:
                    logger.info(f"HERO request failure: {url}")

            for ref in results:
                self.content.append(parse_article(ref))
        self.failures = self._get_missing_ids()
        return dict(success=self.content, failure=self.failures)

    def _get_missing_ids(self) -> list[int]:
        requested_ids = set(self.ids)
        found_ids = set([v["HEROID"] for v in self.content])
        missing = sorted(list(requested_ids - found_ids))
        return missing
