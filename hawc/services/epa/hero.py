import json
import logging
from typing import Any, Dict, List, Optional

import requests

from . import utils


def _parse_pseudo_json(d: Dict, field: str) -> Any:
    # built-in json parser doesn't identify nulls in HERO returns
    v = d.get(field, None)
    if v == "null":
        return None
    else:
        return v


def _force_int(val, default=None) -> Optional[int]:
    try:
        return int(val)
    except Exception:
        return default


def parse_article(content: Dict) -> Dict:
    authors = utils.normalize_authors(content.get("AUTHORS", "").split("; "))
    authors_short = utils.get_author_short_text(authors)
    return dict(
        json=content,
        HEROID=_force_int(_parse_pseudo_json(content, "REFERENCE_ID")),
        PMID=_force_int(_parse_pseudo_json(content, "PMID")),
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

    def __init__(self, id_list: List[int], **kwargs):
        if id_list is None:
            raise Exception("List of IDs are required for a PubMed search")
        self.ids = id_list
        self.ids_count = len(id_list)
        self.content: List[Dict] = []
        self.failures: List[int] = []
        self.settings = HEROFetch.default_settings.copy()
        for k, v in kwargs.items():
            self.settings[k] = v

    def get_content(self):
        rng = list(range(0, self.ids_count, self.settings["recordsperpage"]))
        for recstart in rng:
            request_ids = self.ids[recstart : recstart + self.settings["recordsperpage"]]
            ids = ",".join([str(id_) for id_ in request_ids])
            rpp = self.settings["recordsperpage"]
            url = f"https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/{ids}/recordsperpage/{rpp}.json"
            try:
                r = requests.get(url, timeout=30.0)
                if r.status_code == 200:
                    data = json.loads(r.text)
                    for ref in data["results"]:
                        self.content.append(parse_article(ref))
                else:
                    logging.info(f"HERO request failure: {url}")
            except requests.exceptions.Timeout:
                logging.info(f"HERO request timeout: {url}")
        self.failures = self._get_missing_ids()
        return dict(success=self.content, failure=self.failures)

    def _get_missing_ids(self) -> List[int]:
        requested_ids = set(self.ids)
        found_ids = set([v["HEROID"] for v in self.content])
        missing = sorted(list(requested_ids - found_ids))
        return missing
