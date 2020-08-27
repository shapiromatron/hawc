import base64
import logging
from typing import Dict, Optional

import requests
from django.urls import NoReverseMatch, reverse

logger = logging.getLogger(__name__)


def get_cache_name(cas_number: str) -> str:
    return f"casrn-{cas_number.replace(' ', '-')}"


def get_casrn_url(casrn: str) -> Optional[str]:
    try:
        return reverse("assessment:casrn_detail", args=(casrn,))
    except NoReverseMatch:
        return None


def fetch_dsstox(casrn: str) -> Dict:
    d = {"status": "failed", "content": {}}
    try:
        # get details
        url = r"https://actorws.epa.gov/actorws/chemIdentifier/v01/resolve.json"
        params = {"identifier": casrn}
        response_dict = requests.get(url, params).json()["DataRow"]

        dtxsid = response_dict["dtxsid"]
        content = dict(
            casrn=casrn,
            common_name=response_dict["preferredName"],
            smiles=response_dict["smiles"],
            mw=response_dict["molWeight"],
            dtxsid=dtxsid,
            url_dashboard=f"https://comptox.epa.gov/dashboard/dsstoxdb/results?search={dtxsid}",
        )

        # get image
        url = r"https://actorws.epa.gov/actorws/chemical/image"
        params = {"casrn": casrn, "fmt": "jpeg"}
        response = requests.get(url, params)
        content["image"] = base64.b64encode(response.content).decode("utf-8")

        # call it a success if we made it here
        d["status"] = "success"
        d["content"] = content

    except AttributeError:
        logger.error(f"Request failed: {response.text}", exc_info=True)

    except Exception as e:
        logger.error(str(e), exc_info=True)

    return d
