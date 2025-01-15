import logging
import random
import re
import xml.etree.ElementTree as ET
from itertools import chain

from django.conf import settings

from ..utils.authors import get_author_short_text, normalize_author
from ..utils.sessions import get_session

logger = logging.getLogger(__name__)


class PubMedSearch:
    """Search PubMed with search-term and return a complete list of PubMed IDs."""

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    default_data = dict(db="pubmed", retmode="xml")
    retmax = 5000

    def __init__(self, term: str):
        self.id_count: int | None = None
        self.term = term
        self.session = get_session()

    def get_payload(self, extra: dict | None = None) -> dict:
        payload = self.default_data.copy()
        payload["term"] = self.term
        if settings.PUBMED_API_KEY:
            payload["api_key"] = settings.PUBMED_API_KEY
        if extra:
            payload.update(extra)
        return payload

    def _get_id_count(self) -> int:
        if settings.HAWC_FEATURES.FAKE_IMPORTS:
            return 1

        payload = self.get_payload(extra=dict(rettype="count"))
        response = self.session.post(PubMedSearch.base_url, data=payload, timeout=15)
        if response.status_code == 200:
            txt = ET.fromstring(response.text)
            logger.info(f"{self.id_count} references found")
            return int(txt.find("Count").text)
        else:
            raise Exception("Search query failed; please reformat query or try again later")

    def _parse_ids(self, tree: str) -> list[int]:
        return [int(id.text) for id in ET.fromstring(tree).find("IdList").findall("Id")]

    def _fetch_ids(self):
        if settings.HAWC_FEATURES.FAKE_IMPORTS:
            self.ids = [random.randrange(100_000_000, 999_9999_999)]  # noqa: S311
            return

        ids = []
        payload = self.get_payload(extra=dict(retmax=self.retmax))
        if self.id_count is None:
            self._get_id_count()
        rng = list(range(0, self.id_count, self.retmax))
        self.request_count = len(rng)
        for retstart in rng:
            payload["retstart"] = retstart
            resp = self.session.post(PubMedSearch.base_url, data=payload, timeout=15)
            if resp.status_code == 200:
                ids.extend(self._parse_ids(resp.text))
            else:
                raise Exception("Search query failed; please reformat query or try again later")
        self.ids = ids

    def get_ids_count(self) -> int:
        self.id_count = self._get_id_count()
        return self.id_count

    def get_ids(self) -> list[int]:
        self._fetch_ids()
        return self.ids

    def get_changes_from_previous_search(self, old_ids_list):
        """Return a dictionary with additions and removals of PMIDs."""
        return {
            "added": set(self.ids) - set(old_ids_list),
            "removed": set(old_ids_list) - set(self.ids),
        }


class PubMedFetch:
    """Given a list of PubMed IDs, return list of dict of PubMed citation."""

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    default_data = dict(retmax=1000, db="pubmed", retmode="xml")

    def __init__(self, id_list: list[int], **kwargs):
        super().__init__()
        self.ids = id_list
        self.content: list[dict] = []
        self.session = get_session()

    def get_payload(self, extra: dict | None = None) -> dict:
        payload = self.default_data.copy()
        if settings.PUBMED_API_KEY:
            payload["api_key"] = settings.PUBMED_API_KEY
        if extra:
            payload.update(extra)
        return payload

    def fake(self) -> list[dict]:
        return [
            {
                "xml": "",
                "PMID": id,
                "title": "Reference Title",
                "abstract": "",
                "citation": "citation",
                "year": 2021,
                "doi": "10.",
                "authors": ["author 1", "author 2"],
                "authors_short": "Author 1 and Author 2",
            }
            for id in self.ids
        ]

    def get_content(self) -> list[dict]:
        payload = self.get_payload()
        rng = list(range(0, len(self.ids), payload["retmax"]))
        self.request_count = len(rng)
        for retstart in rng:
            if settings.HAWC_FEATURES.FAKE_IMPORTS:
                self.content = self.fake()
                break

            payload["id"] = self.ids[retstart : retstart + payload["retmax"]]
            resp = self.session.post(PubMedFetch.base_url, data=payload, timeout=15)
            if resp.status_code == 200:
                tree = ET.fromstring(resp.text.encode("utf-8"))
                if tree.tag != "PubmedArticleSet":
                    raise ValueError(f"Unexpected response type: {tree.tag}")
                for content in tree:
                    result = PubMedParser.parse(content)
                    if result:
                        self.content.append(result)
            else:
                logger.error(f"Pubmed failure: {resp.status_code} -> {resp.text}")
                logger.error(f"Pubmed failure data submission: {payload}")
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
    def parse(cls, tree: ET.Element) -> dict | None:
        if tree.tag == "PubmedArticle":
            return cls._parse_article(tree)
        elif tree.tag == "PubmedBookArticle":
            return cls._parse_book(tree)
        else:
            logger.warning(f"Cannot parse response: {tree.tag}")
            return None

    @classmethod
    def _parse_article(cls, tree: ET.Element) -> dict:
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
    def _parse_book(cls, tree: ET.Element) -> dict:
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
    def _authors_info(cls, tree: ET.Element, dtype) -> dict:
        names = []
        auths = []
        if dtype == cls.ARTICLE:
            auths = tree.findall("MedlineCitation/Article/AuthorList/Author")
        elif dtype == cls.BOOK:
            auths = chain(
                tree.findall('BookDocument/Book/AuthorList[@Type="authors"]/Author'),
                tree.findall('BookDocument/AuthorList[@Type="authors"]/Author'),
            )
        else:
            logger.error(f"Unknown dtype: {dtype}")

        for auth in auths:
            last = auth.find("LastName")
            collective = auth.find("CollectiveName")
            if last is not None:
                initials = cls._try_single_find(auth, "Initials")
                names.append(normalize_author(f"{last.text} {initials}".strip()))
            elif collective is not None:
                names.append(collective.text)
            else:
                text = ET.tostring(auth, encoding="unicode")
                logger.error(f"Error parsing authors: {text}")

        return {"authors": names, "authors_short": get_author_short_text(names)}

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
    def _get_year(cls, tree: ET.Element, dtype) -> int | None:
        if dtype == cls.ARTICLE:
            year = tree.find("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
            if year is not None:
                return int(year.text)

            medline_date = tree.find(
                "MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate"
            )
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
    def _get_doi(cls, tree: ET.Element, search_string) -> str | None:
        doi = tree.find(search_string)
        if doi is not None:
            return doi.text.lower()
        else:
            return None
