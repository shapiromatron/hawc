import re
import logging
import xml.etree.ElementTree as ET

from django.conf import settings

import requests


logger = logging.getLogger(__name__)


def fetch_chemspider(cas_number):
    d = {}
    try:
        # get chemspider chem id
        url = 'http://www.chemspider.com/Search.asmx/SimpleSearch'
        payload = {
            'query': cas_number,
            'token': settings.CHEMSPIDER_TOKEN,
        }
        r = requests.post(url, data=payload)

        id_val = re.search(r'\<int\>(\d+)\</int\>', r.content).group(1)

        # get details
        url = 'http://www.chemspider.com/MassSpecAPI.asmx/GetExtendedCompoundInfo'  # noqa
        payload = {
            'CSID': id_val,
            'token': settings.CHEMSPIDER_TOKEN,
        }
        r = requests.post(url, data=payload)
        xml = ET.fromstring(r.content)
        namespace = '{http://www.chemspider.com/}'
        d['CommonName'] = xml.find('{}CommonName'.format(namespace)).text
        d['SMILES'] = xml.find('{}SMILES'.format(namespace)).text
        d['MW'] = xml.find('{}MolecularWeight'.format(namespace)).text

        # get image
        url = 'http://www.chemspider.com/Search.asmx/GetCompoundThumbnail'
        payload = {
            'id': id_val,
            'token': settings.CHEMSPIDER_TOKEN,
        }
        r = requests.post(url, data=payload)
        xml = ET.fromstring(r.content)
        d['image'] = xml.text

        # call it a success if we made it here
        d['status'] = 'success'

    except Exception as e:
        logger.error(e.message, exc_info=True)

    return d
