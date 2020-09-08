import logging
import re
import xml.etree.ElementTree as ET
from itertools import chain
from typing import Dict, List, Optional

import requests

from . import utils


class PubMedSettings:
    """Module-level settings to check that PubMed requests registered."""

    PLACEHOLDER = "PLACEHOLDER"

    def __init__(self):
        self.api_key = self.PLACEHOLDER

    def connect(self, api_key: str):
        self.api_key = api_key


# global singleton
settings = PubMedSettings()


def connect(api_key: str):
    settings.connect(api_key)


class PubMedUtility:
    """Register tools with this utility class to import PubMed settings."""

    def _register_instance(self):
        if settings.api_key != PubMedSettings.PLACEHOLDER:
            self.settings["api_key"] = settings.api_key


class PubMedSearch(PubMedUtility):
    """Search PubMed with search-term and return a complete list of PubMed IDs."""

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    default_settings = dict(retmax=5000, db="pubmed")

    def __init__(self, term, **kwargs):
        self.id_count = None
        self.settings = PubMedSearch.default_settings.copy()
        self._register_instance()
        self.settings["term"] = term
        for k, v in kwargs.items():
            self.settings[k] = v

    def _get_id_count(self):
        data = dict(db=self.settings["db"], term=self.settings["term"], rettype="count")
        r = requests.post(PubMedSearch.base_url, data=data)
        if r.status_code == 200:
            txt = ET.fromstring(r.text)
            self.id_count = int(txt.find("Count").text)
            logging.info(f"{self.id_count} references found")
        else:
            raise Exception("Search query failed; please reformat query or try again later")

        return self.id_count

    def _parse_ids(self, tree: str) -> List[int]:
        return [int(id.text) for id in ET.fromstring(tree).find("IdList").findall("Id")]

    def _fetch_ids(self):
        ids = []
        data = self.settings.copy()
        if self.id_count is None:
            self._get_id_count()
        rng = list(range(0, self.id_count, self.settings["retmax"]))
        self.request_count = len(rng)
        for retstart in rng:
            data["retstart"] = retstart
            resp = requests.post(PubMedSearch.base_url, data=data)
            if resp.status_code == 200:
                ids.extend(self._parse_ids(resp.text))
            else:
                raise Exception("Search query failed; please reformat query or try again later")
        self.ids = ids

    def get_ids_count(self) -> int:
        return self._get_id_count()

    def get_ids(self) -> List[int]:
        self._fetch_ids()
        return self.ids

    def get_changes_from_previous_search(self, old_ids_list):
        """Return a dictionary with additions and removals of PMIDs."""
        return {
            "added": set(self.ids) - set(old_ids_list),
            "removed": set(old_ids_list) - set(self.ids),
        }


class PubMedFetch(PubMedUtility):
    """Given a list of PubMed IDs, return list of dict of PubMed citation."""

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    default_settings = dict(retmax=1000, db="pubmed", retmode="xml")

    def __init__(self, id_list, **kwargs):
        if id_list is None:
            raise Exception("List of IDs are required for a PubMed search")
        self.ids = id_list
        self.content: List[Dict] = []
        self.settings = PubMedFetch.default_settings.copy()
        self._register_instance()
        for k, v in kwargs.items():
            self.settings[k] = v

    def get_content(self) -> List[Dict]:
        data = self.settings.copy()
        rng = list(range(0, len(self.ids), self.settings["retmax"]))
        self.request_count = len(rng)
        for retstart in rng:
            data["id"] = self.ids[retstart : retstart + self.settings["retmax"]]
            resp = requests.post(PubMedFetch.base_url, data=data)
            if resp.status_code == 200:
                tree = ET.fromstring(resp.text.encode("utf-8"))
                if tree.tag != "PubmedArticleSet":
                    raise ValueError(f"Unexpected response type: {tree.tag}")
                for content in tree.getchildren():
                    result = PubMedParser.parse(content)
                    if result:
                        self.content.append(result)
            else:
                logging.error(f"Pubmed failure: {resp.status_code} -> {resp.text}")
                logging.error(f"Pubmed failure data submission: {data}")
                raise Exception("Fetch query failed; please reformat query or try again later")
        return self.content


class PubMedParser:

    ARTICLE = 0
    BOOK = 1

    DOI_ARTICLE_SEARCH_STRING = 'MedlineCitation/Article/ELocationID[@EIdType="doi"]'
    ABSTRACT_ARTICLE_SEARCH_STRING = "MedlineCitation/Article/Abstract/AbstractText"

    DOI_BOOK_SEARCH_STRING = 'BookDocument/ArticleIdList/ArticleId[@IdType="doi"]'
    ABSTRACT_BOOK_SEARCH_STRING = "BookDocument/Abstract/AbstractText"

    @classmethod
    def parse(cls, tree: ET.Element) -> Optional[Dict]:
        if tree.tag == "PubmedArticle":
            return cls._parse_article(tree)
        elif tree.tag == "PubmedBookArticle":
            return cls._parse_book(tree)
        else:
            logging.warning(f"Cannot parse response: {tree.tag}")
            return None

    @classmethod
    def _parse_article(cls, tree: ET.Element) -> Dict:
        d = {
            "xml": ET.tostring(tree, encoding="unicode"),
            "PMID": int(cls._try_single_find(tree, "MedlineCitation/PMID")),
            "title": cls._try_single_find(tree, "MedlineCitation/Article/ArticleTitle"),
            "abstract": cls._get_abstract(tree, cls.ABSTRACT_ARTICLE_SEARCH_STRING),
            "citation": cls._journal_info(tree),
            "year": cls._get_year(tree, dtype=cls.ARTICLE),
            "doi": cls._get_doi(tree, cls.DOI_ARTICLE_SEARCH_STRING),
        }
        d.update(cls._authors_info(tree, cls.ARTICLE))
        return d

    @classmethod
    def _parse_book(cls, tree: ET.Element) -> Dict:
        pmid = int(cls._try_single_find(tree, "BookDocument/PMID"))
        book_title = cls._try_single_find(tree, "BookDocument/Book/BookTitle")
        article_title = cls._try_single_find(tree, "BookDocument/ArticleTitle")
        abstract = cls._get_abstract(tree, cls.ABSTRACT_BOOK_SEARCH_STRING)
        year = cls._get_year(tree, dtype=cls.BOOK)
        doi = cls._get_doi(tree, cls.DOI_BOOK_SEARCH_STRING)

        d = {
            "xml": ET.tostring(tree, encoding="unicode"),
            "PMID": pmid,
            "abstract": abstract,
            "year": year,
            "doi": doi,
        }
        d.update(cls._authors_info(tree, cls.BOOK))

        if article_title:
            d["title"] = article_title
            d["citation"] = cls._get_book_citation(tree, title=book_title)
        else:
            d["title"] = book_title
            d["citation"] = cls._get_book_citation(tree)

        return d

    @classmethod
    def _get_abstract(cls, tree: ET.Element, search_string) -> str:
        txt = ""

        abstracts = tree.findall(search_string)

        # standard abstract
        if len(abstracts) == 1:
            txt = "".join([txt for txt in abstracts[0].itertext()])

        # structured abstract
        if len(abstracts) > 1:
            txts = []
            for abstract in abstracts:
                tmp = "".join([txt for txt in abstract.itertext()])
                lbl = abstract.attrib.get("Label")
                if lbl:
                    tmp = f'<span class="abstract_label">{lbl}: </span>' + tmp
                txts.append(tmp)
            txt = "<br>".join(txts)
        return txt

    @classmethod
    def _try_single_find(cls, tree: ET.Element, search) -> str:
        try:
            match = tree.find(search)
            return "".join([txt for txt in match.itertext()])
        except Exception:
            return ""

    @classmethod
    def _authors_info(cls, tree: ET.Element, dtype) -> Dict:
        names = []

        if dtype == cls.ARTICLE:
            auths = tree.findall("MedlineCitation/Article/AuthorList/Author")
        elif dtype == cls.BOOK:
            auths = chain(
                tree.findall('BookDocument/Book/AuthorList[@Type="authors"]/Author'),
                tree.findall('BookDocument/AuthorList[@Type="authors"]/Author'),
            )

        for auth in auths:
            try:
                names.append(
                    utils.normalize_author(
                        f"{auth.find('LastName').text} {auth.find('Initials').text}"
                    )
                )
            except Exception:
                pass

            try:
                names.append(auth.find("CollectiveName").text)
            except Exception:
                pass

        return {"authors": names, "authors_short": utils.get_author_short_text(names)}

    @classmethod
    def _journal_info(cls, tree: ET.Element) -> str:
        journal = cls._try_single_find(tree, "MedlineCitation/Article/Journal/ISOAbbreviation")
        year = cls._try_single_find(
            tree, "MedlineCitation/Article/Journal/JournalIssue/PubDate/Year"
        )
        volume = cls._try_single_find(tree, "MedlineCitation/Article/Journal/JournalIssue/Volume")
        issue = cls._try_single_find(tree, "MedlineCitation/Article/Journal/JournalIssue/Issue")
        pages = cls._try_single_find(tree, "MedlineCitation/Article/Pagination/MedlinePgn")
        return f"{journal} {year}; {volume} ({issue}):{pages}"

    @classmethod
    def _get_book_citation(cls, tree: ET.Element, title=None) -> str:
        if title:
            title += " "
        else:
            title = ""

        year = cls._try_single_find(tree, "BookDocument/Book/PubDate/Year")
        location = cls._try_single_find(tree, "BookDocument/Book/Publisher/PublisherLocation")
        publisher = cls._try_single_find(tree, "BookDocument/Book/Publisher/PublisherName")
        return f"{title}({year}). {location}: {publisher}."

    @classmethod
    def _get_year(cls, tree: ET.Element, dtype) -> Optional[int]:
        if dtype == cls.ARTICLE:
            year = tree.find("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
            if year is not None:
                return int(year.text)

            medline_date = tree.find(
                "MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate"
            )  # noqa
            if medline_date is not None:
                year = re.search(r"(\d+){4}", medline_date.text)
                if year is not None:
                    return int(year.group(0))

            return None

        elif dtype == cls.BOOK:
            year = tree.find("BookDocument/Book/PubDate/Year")
            if year is not None:
                return int(year.text)

            return None
        else:
            raise ValueError("Unreachable code")
            return None

    @classmethod
    def _get_doi(cls, tree: ET.Element, search_string) -> Optional[str]:
        doi = tree.find(search_string)
        if doi is not None:
            return doi.text
        else:
            return None
