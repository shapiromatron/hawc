# -*- coding: utf-8 -*-
"""Query UMLS.

@author: scott
"""

import requests
from lxml.html import fromstring
import json
import time


class Authentication:
    """Get api token."""

    def __init__(self, apikey):
        """Init method."""
        self.apikey = apikey
        self.service = "http://umlsks.nlm.nih.gov"
        self.uri = "https://utslogin.nlm.nih.gov"
        self.auth_endpoint = "/cas/v1/api-key"
        self.tgt = None
        self.tgt_time = None
        self.gettgt()

    def gettgt(self):
        """Get tgt."""
        params = {'apikey': self.apikey}
        h = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/plain", "User-Agent": "python"}
        r = requests.post(self.uri+self.auth_endpoint, data=params, headers=h)
        response = fromstring(r.text)
        tgt = response.xpath('//form/@action')[0]
        self.tgt_time = time.time()
        self.tgt = tgt

    def tgt_check(self):
        """Check to see if tgt is expired."""
        now = time.time()
        if now-self.tgt_time > (28800-300):
            self.gettgt()

    def getst(self):
        """Get single use token."""
        self.tgt_check()
        params = {'service': self.service}
        h = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/plain", "User-Agent": "python"}
        r = requests.post(self.tgt, data=params, headers=h)
        st = r.text
        return st


class SearchCUI:
    """Get info for a CUI."""

    def __init__(self, CUI, auth):
        """Init."""
        self.cui = CUI
        self.auth = auth
        self.uri = 'https://uts-ws.nlm.nih.gov/rest'
        self.endpoint = '/content/current/CUI/'

        self.id = self.cui
        self.name = None
        self.synonyms = None

    def getinfo(self):
        """Get info for CUI."""
        params = {'ticket': self.auth.getst()}
        r = requests.get(self.uri + self.endpoint + self.cui, params=params)
        if r.status_code != 200:
            return None
        d = json.loads(r.text)
        # return d
        self._parse_data(d['result'])

    def _parse_data(self, res):
        """Pasrse json for info."""
        self.name = res['name']
        atom_url = res['atoms']
        if atom_url is not None and atom_url.lower() != 'none':
            self.synonyms = self._get_synonyms(atom_url)

    def _get_synonyms(self, url):
        """Get synonyms for CUI."""
        result_list = []
        for i in range(1, 20):
            params = {'ticket': self.auth.getst(), 'language': 'ENG',
                      'pageNumber': i}
            r = requests.get(url, params=params)
            if r.status_code != 200:
                break
            rd = json.loads(r.text)
            result_list += rd['result']
            if rd['pageNumber'] == rd['pageCount']:
                break
        if not result_list:
            return None
        result_list = [i['name'] for i in result_list if i['name'] is not None
                       and i['name'].lower() != 'none']
        return set(result_list)


auth = Authentication('6d992c4d-eb34-4aa0-9323-c562532fce8d')

s = SearchCUI('C0006121', auth)
d = s.getinfo()
