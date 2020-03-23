import base64
import logging

import requests

logger = logging.getLogger(__name__)


def fetch_dsstox(cas_number):
    d = {}
    try:
        # get details
        url = r"https://actorws.epa.gov/actorws/chemIdentifier/v01/resolve.json"
        params = {"identifier": cas_number}
        response_dict = requests.get(url, params).json()["DataRow"]
        d["CommonName"] = response_dict["preferredName"]
        d["SMILES"] = response_dict["smiles"]
        d["MW"] = response_dict["molWeight"]
        d["DTXSID"] = response_dict["dtxsid"]

        # get image
        url = r"https://actorws.epa.gov/actorws/chemical/image"
        params = {"casrn": cas_number, "fmt": "jpeg"}
        response = requests.get(url, params)
        d["image"] = base64.b64encode(response.content).decode("utf-8")

        # call it a success if we made it here
        d["status"] = "success"

    except AttributeError:
        logger.error(f"Request failed: {response.text}", exc_info=True)

    except Exception as e:
        logger.error(str(e), exc_info=True)

    return {} if d["DTXSID"] is None else d
