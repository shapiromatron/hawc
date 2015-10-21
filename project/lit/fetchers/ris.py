import re
from copy import copy
import logging
import json

from RISparser import readris
from RISparser.config import TAG_KEY_MAPPING

from .utils import get_author_short_text


class RisImporter(object):

    def custom_mapping(self):
        mapping = copy(TAG_KEY_MAPPING)
        mapping.update({
            "AT": "accession_type",
            "PM": "pubmed_id",
            'N2': "abstract2",
        })
        return mapping

    def __init__(self, fn):
        with open(fn, 'r') as f:
            reader = readris(f, mapping=self.custom_mapping())
            contents = [content for content in reader]
        self.contents = contents

    def format(self):
        formatted_content = []
        for content in self.references:
            parser = ReferenceParser(content)
            formatted_content.append(parser.format())
        return formatted_content

    def to_excel(self):
        formatted = self.format()
        print formatted + " to Excel."


class ReferenceParser(object):

    PLACEHOLDER_TEXT = "<ADD>"

    # field types
    TITLE_FIELDS = (
        'translated_title', 'title', 'primary_title',
        'secondary_title', 'tertiary_title', 'short_title',
    )

    AUTHOR_LIST_FIELDS = (
        'authors', 'first_authors', 'secondary_authors',
        'tertiary_authors', 'subsidiary_authors',
    )

    ABSTRACT_FIELDS = ('abstract', 'abstract2', )

    YEAR_FIELDS = ("year", "publication_year", )

    # publication types
    JOURNAL_TYPES = ('Journal (full)', 'Journal', )

    # First-group is rest of reference; second-group are initials
    # with optional second initial (middle-name) with optional periods
    re_author = re.compile(
        r"([-\w]+)\s(\w\.\s*(?:\w{1,1}\.?)?)$",
        flags=re.UNICODE
    )

    # Match any number (some PMIDs contain number and/or URL)
    re_pmid = re.compile(r"([\d]+)")

    def __init__(self, content):
        self.content = content

    def format(self, article):
        if getattr(self, "_formatted") is None:
            self._formatted = {
                "authors_short": self._get_authors_short(),
                "title": self._get_field(self.TITLE_FIELDS, self.PLACEHOLDER_TEXT),
                "year": self.self._get_field(self.TITLE_FIELDS, None),
                "citation": self._get_citation(),
                "abstract": self._get_field(self.ABSTRACT_FIELDS, ""),
                "PMID":  self._get_pmid(),
                "doi": self.context.get("doi", None),
                "accession_number": self.context.get("accession_number", None),
                "accession_db": self.context.get("name_of_database", None),
                "json": json.dumps(self.content),
            }
        return self._formatted

    def _get_field(self, fields, default):
        for fld in fields:
            if fld in self.content:
                return self.content.get(fld)
        return default

    def _get_pmid(self):
        # get PMID if specified in that field
        if "pubmed_id" in self.context:
            pubmed_id = self.context["pubmed_id"]
            if type(pubmed_id) is int:
                return pubmed_id
            else:
                m = self.re_pmid.findall(pubmed_id)
                if len(m) > 0:
                    # no try/catch req'd; return first matching int
                    return int(m[0])

        # get value accession number is NLM
        if (self.context.get("name_of_database", "") == "NLM" and
                "accession_number" in self.context):
            try:
                return int(self.context['accession_number'])
            except ValueError:
                pass

        return None

    def _clean_authors(self):
        self._authors = []
        for fld in self.AUTHOR_LIST_FIELDS:
            if fld in self.content:
                for author in self.content[fld]:
                    # attempt changing "Smith D. L." to "Smith DL"
                    txt = author
                    m = self.re_author.match(author)
                    if m:
                        initials = re.sub(r"[\s\.]", "", m.group(2))
                        txt = u"{0} {1}".format(m.group(1), initials)
                    self._authors.append(txt)

    def _get_authors_short(self):
        if not getattr(self, "_authors"):
            self._clean_authors()
        return get_author_short_text(self._authors)

    def _get_citation(self):
        refType = self.content.get("type_of_reference", "")
        citation = self.PLACEHOLDER_TEXT
        if refType in self.JOURNAL_TYPES:
            citation = u'{0} {1}; {2} ({3}):{4}'.format(*(
                self.content.get("alternate_title1", ""),  # journal
                self.content.get("year", ""),              # year
                self.content.get("volume", ""),            # volume
                self.content.get("note", ""),              # issue
                self.content.get("start_page", ""),        # pages
            ))
        elif refType == "Book chapter":
            vals = []
            if "secondary_title" in self.content:
                vals.append(u"{0}.".format(self.content["secondary_title"]))
            if "year" in self.content:
                vals.apend(u"{0}.".format(self.content["year"]))
            if "start_page" in self.content:
                vals.append(u"Pages {0}.".format(self.content["start_page"]))
            if "issn" in self.content:
                vals.append(u"{0}".format(self.content["issn"]))
            citation = u" ".join(vals)
        else:
            id_ = self.content.get('id', None)
            logging.warning('Unknown type: "{}", id="{}"'.format(refType, id_))
        return citation
