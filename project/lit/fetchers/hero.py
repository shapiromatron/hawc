import logging
import json

import requests

from .general import get_author_short_text


"""
HERO API (example function call):
GET http://hero.epa.gov/ws/index.cfm/api/1.0/search/heroid/1203

All query fields are passed as name/value pairs in the URL. For example:

JSON
http://hero.epa.gov/ws/index.cfm/api/1.0/search/criteria/mercury.json
http://hero.epa.gov/ws/index.cfm/api/1.0/search/singleyear/1990/any/inhalation

XML
http://hero.epa.gov/ws/index.cfm/api/1.0/search/criteria/mercury.xml
http://hero.epa.gov/ws/index.cfm/api/1.0/search/singleyear/1990/any/inhalation%20reference.xml
http://hero.epa.gov/ws/index.cfm/api/1.0/search/singleyear/1990/any/inhalation%20reference/recordsperpage/5.xml

RIS
http://hero.epa.gov/ws/index.cfm/api/1.0/search/criteria/mercury.ris

Getting multiple HERO ids (records per page required)
http://hero.epa.gov/ws/index.cfm/api/1.0/search/criteria/1200,1201,1203,1204/recordsperpage/500.xml

"""

class HEROFetch(object):
    """
    Given a list of HERO IDs, fetch the content for each one and return a
    list of dictionaries of citation information. Note that this citation
    includes the PubMed id, if that's present in HERO
    """
    base_url = r'http://hero.epa.gov/ws/index.cfm/api/1.0/search/criteria/{pks}/recordsperpage/{rpp}.json'
    default_settings = {'recordsperpage': 100}

    def __init__(self, id_list, **kwargs):
        if id_list is None:
            raise Exception('List of IDs are required for a PubMed search')
        self.ids = id_list
        self.ids_count = len(id_list)
        self.content = []
        self.failures = []
        self.settings = HEROFetch.default_settings.copy()
        for k, v in kwargs.iteritems():
            self.settings[k] = v

    def get_content(self):
        rng = range(0, self.ids_count, self.settings['recordsperpage'])
        for recstart in rng:
            pks = ','.join([str(pk) for pk in
                           self.ids[recstart:recstart+self.settings['recordsperpage']]])
            url = HEROFetch.base_url.format(pks=pks, rpp=self.settings['recordsperpage'])
            try:
                r = requests.get(url, timeout=30.)
                if r.status_code == 200:
                    data = json.loads(r.text)
                    for ref in data["RESULTS"]:
                        self.content.append(self._parse_article(ref))
                else:
                    self.failures.extend([int(pk) for pk in pks.split(',')])
                    logging.info("HERO request failure: {url}".format(url=url))
            except requests.exceptions.Timeout:
                self.failures.extend([int(pk) for pk in pks.split(',')])
                logging.info("HERO request timeout: {url}".format(url=url))
        self._get_missing_HEROIDS()
        return {"success": self.content, "failure": self.failures}

    def _get_missing_HEROIDS(self):
        found_ids = set([v['HEROID'] for v in self.content])
        needed_ids = set(self.ids)
        missing=list(needed_ids-found_ids)
        if len(missing)>0:
            self.failures.extend(missing)

    def _force_float_or_none(self, val):
        try:
            return float(val)
        except:
            return None

    def _parse_pseudo_json(self, d, field):
        # built-in json parser doesn't identify nulls in HERO returns
        v = d.get(field, None)
        if v == u'null':
            return None
        else:
            return v

    def _parse_article(self, article):
        d = {"json": json.dumps(article, encoding='utf-8'),
             "HEROID": self._parse_pseudo_json(article, 'REFERENCE_ID'),
             "PMID": self._parse_pseudo_json(article, 'PMID'),
             "title": self._parse_pseudo_json(article, 'TITLE'),
             "abstract": self._parse_pseudo_json(article, 'ABSTRACT'),
             "source": self._parse_pseudo_json(article, 'SOURCE'),
             "year":  self._force_float_or_none(self._parse_pseudo_json(article, 'YEAR'))}
        logging.debug('Parsing results for HEROID: {heroid}'.format(heroid=d['HEROID']))
        d.update(self._authors_info(article.get('AUTHORS', None)))
        return d

    @classmethod
    def _try_single_find(cls, xml, search):
        try:
            return xml.find(search).text
        except:
            return ''

    def _authors_info(self, names_string):
        names = []
        if names_string:
            names = names_string.split('; ')
            names = [name.replace(', ', ' ') for name in names]
        return {'authors_list': names,
                'authors_short': get_author_short_text(names)}
