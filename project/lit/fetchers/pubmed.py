import logging
import xml.etree.ElementTree as ET
import re

import requests

from .utils import get_author_short_text


"""
PubMed API:
http://www.ncbi.nlm.nih.gov/books/NBK25499/

"""

class PubMedSearch(object):
    """
    Given a search term upon initialization, search PubMed and return a full
    list of PubMed IDs from the selected search term.
    """
    base_url = r'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    default_settings = {"retmax": 5000,
                        "db": "pubmed",
                        "term": "",
                        "tool": "hawc",
                        "email": "ajshapir@email.unc.edu"}

    def __init__(self, **kwargs):
        if not kwargs.get('term'):
            raise Exception('Search "term" is required for a PubMed search')
        self.settings = PubMedSearch.default_settings.copy()
        for k, v in kwargs.iteritems():
            self.settings[k] = v

    def _get_id_count(self):
        data = {"db": self.settings["db"],
                "term": self.settings["term"],
                "rettype": "count"}
        r = requests.post(PubMedSearch.base_url, data=data)
        if r.status_code == 200:
            txt = ET.fromstring(r.text)
            self.id_count = int(txt.find('Count').text)
            logging.info("{c} references found.".format(c=self.id_count))
        else:
            raise Exception("Search query failed; please reformat query or try again later")

    def _parse_ids(self, txt):

        def parse_id(xml):
            return int(xml.text)

        id_list = ET.fromstring(txt).find("IdList")
        ids = id_list.findall("Id")
        return map(parse_id, ids)

    def _fetch_ids(self):
        ids = []
        data = self.settings.copy()
        rng = range(0, self.id_count, self.settings['retmax'])
        self.request_count = len(rng)
        for retstart in rng:
            data['retstart'] = retstart
            r = requests.post(PubMedSearch.base_url, data=data)
            if r.status_code == 200:
                ids.extend(self._parse_ids(r.text))
            else:
                raise Exception("Search query failed; please reformat query or try again later")
        self.ids = ids

    def get_ids_count(self):
        self._get_id_count()

    def get_ids(self):
        self._fetch_ids()
        return self.ids

    def get_changes_from_previous_search(self, old_ids_list):
        """
        Returns a dictionary showing the additions and removals when comparing
        a new search to the old, in set notation.
        """
        return {'added': set(self.ids) - set(old_ids_list),
                'removed': set(old_ids_list) - set(self.ids)}


class PubMedFetch(object):
    """
    Given a list of PubMed IDs, fetch the content for each one and return a
    list of dictionaries of PubMed citation information.
    """
    base_url = r'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    default_settings = {"retmax": 1000,
                        "db": "pubmed",
                        "retmode": "xml",
                        "tool": "hawc",
                        "email": "ajshapir@email.unc.edu"}

    def __init__(self, id_list, **kwargs):
        if id_list is None:
            raise Exception('List of IDs are required for a PubMed search')
        self.ids = id_list
        self.content = []
        self.settings = PubMedFetch.default_settings.copy()
        for k, v in kwargs.iteritems():
            self.settings[k] = v

    def get_content(self):
        data = self.settings.copy()
        rng = range(0, len(self.ids), self.settings['retmax'])
        self.request_count = len(rng)
        for retstart in rng:
            data['id'] = self.ids[retstart: retstart+self.settings['retmax']]
            r = requests.post(PubMedFetch.base_url, data=data)
            if r.status_code == 200:
                articles = ET.fromstring(r.text.encode('utf-8')).findall("PubmedArticle")
                for article in articles:
                    self.content.append(self._parse_article(article))
            else:
                raise Exception("Fetch query failed; please reformat query or try again later")
        return self.content

    def _parse_article(self, article):
        pmid = int(PubMedFetch._try_single_find(article, "MedlineCitation/PMID"))
        logging.debug('Parsing results for PMID: {pmid}'.format(pmid=pmid))
        d = {"xml": ET.tostring(article, encoding='utf-8'),
             "PMID": pmid,
             "title": PubMedFetch._try_single_find(article, "MedlineCitation/Article/ArticleTitle"),
             "abstract": self._get_abstract(article),
             "citation": self._journal_info(article),
             "year": self._get_year(article)}
        d.update(self._authors_info(article))
        return d

    def _get_abstract(self, article):
        txt = ""
        abstracts = article.findall("MedlineCitation/Article/Abstract/AbstractText")

        # standard abstract
        if len(abstracts) == 1:
            txt = abstracts[0].text

        # structured abstract
        if len(abstracts) > 1:
            txts = []
            for abstract in abstracts:
                tmp = abstract.text or u""
                lbl = abstract.attrib.get('Label')
                if lbl:
                    tmp = u"<span class='abstract_label'>{v}: </span>".format(v=lbl) + tmp
                txts.append(tmp)
            txt = u'<br>'.join(txts)
        return txt

    @classmethod
    def _try_single_find(cls, xml, search):
        try:
            return xml.find(search).text
        except:
            return ''

    def _authors_info(self, article):
        names = []
        auths = article.findall('MedlineCitation/Article/AuthorList/Author')
        for auth in auths:
            try:
                names.append(u'{last_name} {initials}'.format(last_name=auth.find('LastName').text,
                                                              initials=auth.find('Initials').text))
            except:
                pass

            try:
                names.append(u'{name}'.format(name=auth.find('CollectiveName').text))
            except:
                pass

        return {'authors_list': names,
                'authors_short': get_author_short_text(names)}

    def _journal_info(self, article):
        return u'{journal} {year}; {volume} ({issue}):{pages}'.format(
            journal=PubMedFetch._try_single_find(article, 'MedlineCitation/Article/Journal/ISOAbbreviation'),
            year=PubMedFetch._try_single_find(article, 'MedlineCitation/Article/Journal/JournalIssue/PubDate/Year'),
            volume=PubMedFetch._try_single_find(article, 'MedlineCitation/Article/Journal/JournalIssue/Volume'),
            issue=PubMedFetch._try_single_find(article, 'MedlineCitation/Article/Journal/JournalIssue/Issue'),
            pages=PubMedFetch._try_single_find(article, 'MedlineCitation/Article/Pagination/MedlinePgn'))

    def _get_year(self, et):
        year = et.find("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
        if year is not None:
            return int(year.text)

        medline_date = et.find("MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate")
        if medline_date is not None:
            year = re.search(r'(\d+){4}', medline_date.text)
            if year is not None:
                return int(year.group(0))
