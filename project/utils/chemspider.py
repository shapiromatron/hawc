import json
import logging
from django.conf import settings
import requests


logger = logging.getLogger(__name__)


def fetch_chemspider(cas_number):
    d = {}
    try:
        with requests.Session() as session:
            session.headers.update({
                'apikey': settings.CHEMSPIDER_TOKEN,
                'Content-type': 'application/json',
                'Accept': 'application/json'
            })

            # submit query
            url = 'https://api.rsc.org/compounds/v1/filter/name'
            payload = {"name": cas_number}
            response = session.post(url, data=json.dumps(payload))
            query_id = response.json()['queryId']

            # get chemspider id
            url = f'https://api.rsc.org/compounds/v1/filter/{query_id}/results'
            params = {'start': 0, 'count': 1}
            response = session.get(url, params=params)
            chemspider_id = response.json()['results'][0]

            # get details
            url = f'https://api.rsc.org/compounds/v1/records/{chemspider_id}/details'
            params = {'fields': 'SMILES,MolecularWeight,CommonName'}
            response = session.get(url, params=params).json()
            d['CommonName'] = response['commonName']
            d['SMILES'] = response['smiles']
            d['MW'] = response['molecularWeight']

            # get image
            url = f'https://api.rsc.org/compounds/v1/records/{chemspider_id}/image'
            response = session.get(url)
            d['image'] = response.json()['image']

            # call it a success if we made it here
            d['status'] = 'success'

    except AttributeError as e:
        logger.error(f"Request failed: {response.text}", exc_info=True)

    except Exception as e:
        logger.error(str(e), exc_info=True)

    return d
