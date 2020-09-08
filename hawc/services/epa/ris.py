import logging
import re
from copy import copy
from typing import Optional

import xlsxwriter
from RISparser import readris
from RISparser.config import TAG_KEY_MAPPING

from . import utils


class RisImporter:
    @classmethod
    def get_mapping(cls):
        mapping = copy(TAG_KEY_MAPPING)
        mapping.update(
            {"AT": "accession_type", "PM": "pubmed_id", "N2": "abstract2", "SV": "serial_volume"}
        )
        return mapping

    @classmethod
    def file_readable(cls, f):
        # ensure that file can be successfully parsed
        try:
            reader = readris(f, mapping=cls.get_mapping())
            [content for content in reader]
            f.seek(0)
            return True
        except IOError as err:
            logging.warning(err)
            return False

    def __init__(self, f):
        if isinstance(f, str):
            f = open(f, "r")
        else:
            f = f
        reader = readris(f, mapping=self.get_mapping())
        contents = [content for content in reader]
        f.close()
        self.raw_references = contents

    @property
    def references(self):
        if not hasattr(self, "_references"):
            self._references = self._format()
        return self._references

    def _format(self):
        formatted_content = []
        for content in self.raw_references:
            parser = ReferenceParser(content)
            formatted_content.append(parser.format())
        return formatted_content

    def to_excel(self, fn):
        header = ReferenceParser.EXTRACTED_FIELDS
        data_rows = []
        for ref in self.references:
            data_rows.append([ref[fld] for fld in header])

        wb = xlsxwriter.Workbook(fn)
        ws = wb.add_worksheet()
        bold = wb.add_format({"bold": True})

        for c, txt in enumerate(header):
            ws.write(0, c, txt, bold)

        for r, row in enumerate(data_rows):
            for c, txt in enumerate(row):
                try:
                    ws.write(r + 1, c, txt)
                except AttributeError:
                    ws.write(r + 1, c, txt)

        wb.close()


class ReferenceParser:

    PLACEHOLDER_TEXT = "<ADD>"

    # field types
    TITLE_FIELDS = (
        "translated_title",
        "title",
        "primary_title",
        "secondary_title",
        "tertiary_title",
        "short_title",
    )

    AUTHOR_LIST_FIELDS = (
        "authors",
        "first_authors",
        "secondary_authors",
        "tertiary_authors",
        "subsidiary_authors",
    )

    ABSTRACT_FIELDS = ("abstract", "abstract2")

    YEAR_FIELDS = ("year", "publication_year")

    # Extract the scopus EID
    re_scopus_eid = re.compile(r"eid=([-\.\w]+)(?:&|$)", flags=re.UNICODE)

    EXTRACTED_FIELDS = [
        "authors_short",
        "authors",
        "title",
        "year",
        "citation",
        "abstract",
        "PMID",
        "doi",
        "accession_number",
        "accession_db",
        "reference_type",
        "id",
        "json",
    ]

    # Match any number (some PMIDs contain number and/or URL)
    re_pmid = re.compile(r"([\d]+)")

    def __init__(self, content):
        self.content = content

    def format(self):
        if not hasattr(self, "_formatted"):
            self._formatted = dict(
                authors_short=self._get_authors_short(),
                authors=self._authors,
                title=self._get_field(self.TITLE_FIELDS, self.PLACEHOLDER_TEXT),
                year=self._get_field(self.YEAR_FIELDS, None),
                citation=self._get_citation(),
                abstract=self._get_field(self.ABSTRACT_FIELDS, ""),
                PMID=self._get_pmid(),
                doi=self.content.get("doi", None),
                accession_number=self._get_accession_number(),
                accession_db=self.content.get("name_of_database", None),
                reference_type=self.content.get("type_of_reference", None),
                id=utils.try_int(self.content["id"]),
                json=self.content,
            )
        return self._formatted

    def _get_field(self, fields, default):
        for fld in fields:
            if fld in self.content:
                return self.content.get(fld)
        return default

    def _get_pmid(self) -> Optional[int]:
        # get PMID if specified in that field
        if "pubmed_id" in self.content:
            pubmed_id = self.content["pubmed_id"]
            if type(pubmed_id) is int:
                return pubmed_id
            else:
                m = self.re_pmid.findall(pubmed_id)
                if len(m) > 0:
                    # no try/catch req'd; return first matching int
                    return int(m[0])

        # get value accession number is NLM
        if self.content.get("name_of_database", "") == "NLM" and "accession_number" in self.content:
            try:
                return int(self.content["accession_number"])
            except ValueError:
                pass

        return None

    def _get_accession_number(self):
        number = self.content.get("accession_number", None)

        # extract the Scopus EID
        if number and isinstance(number, str) and "eid=" in number:
            m = self.re_scopus_eid.findall(number)
            if len(m) > 0:
                number = m[0]

        return number

    def _clean_authors(self):
        authors = []
        for fld in self.AUTHOR_LIST_FIELDS:
            if fld in self.content:
                authors.extend([author for author in self.content[fld]])
        self._authors = utils.normalize_authors(authors)

    def _get_authors_short(self):
        if not hasattr(self, "_authors"):
            self._clean_authors()
        return utils.get_author_short_text(self._authors)

    def _get_journal_citation(self):
        # volume is sometimes blank; only add parens if non-blank
        volume = str(self.content.get("volume", ""))
        if len(volume) > 0:
            volume = f"; {volume}"

        # issue is sometimes blank; only add parens if non-blank
        issue = str(self.content.get("note", ""))
        if len(issue) > 0:
            issue = f" ({issue})"

        # pages is sometimes blank; only add colon if non-blank
        pages = str(self.content.get("start_page", ""))
        if len(pages) > 0:
            pages = f":{pages}"

        sec_title = str(self.content.get("secondary_title", ""))  # journal
        year = self.content.get("year", "")  # year
        return f"{sec_title} {year}{volume}{issue}{pages}"

    def _get_book_citation(self):
        vals = []
        if "secondary_title" in self.content:
            vals.append(f"{self.content['secondary_title']}.")
        if "year" in self.content:
            vals.append(f"{self.content['year']}.")
        if "start_page" in self.content:
            vals.append(f"Pages {self.content['start_page']}.")
        if "issn" in self.content:
            vals.append(f"{self.content['issn']}")
        return " ".join(vals)

    def _get_citation(self):
        refType = self.content.get("type_of_reference", "")
        citation = self.PLACEHOLDER_TEXT
        if refType in ("JFULL", "JOUR"):
            citation = self._get_journal_citation()
        elif refType in ("BOOK", "CHAP"):
            citation = self._get_book_citation()
        elif refType == "SER":
            citation = self.content.get("alternate_title1", "")
        elif refType == "CONF":
            citation = self.content.get("short_title", "")
        else:
            id_ = self.content.get("id", None)
            logging.warning(f'Unknown type: "{refType}", id="{id_}"')
        return citation
