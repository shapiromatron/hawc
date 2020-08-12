import base64
import json
import logging
from typing import Dict, Optional

import requests
from django.urls import NoReverseMatch, reverse

logger = logging.getLogger(__name__)


def get_cache_name(dtxsid: str) -> str:
    return f"dtxsid-{dtxsid.replace(' ', '-')}"


def get_dsstox_url(dtxsid: str) -> Optional[str]:
    try:
        return reverse("assessment:dsstox_detail", args=(dtxsid,))
    except NoReverseMatch:
        return None


def fetch_dsstox(dtxsid: str) -> Dict:
    from hawc.apps.assessment.models import DSSTox

    d = {"status": "failed", "content": {}}
    try:
        # get details
        dsstox = DSSTox.objects.get(pk=dtxsid)
        # loaded as text in test database; parse dict from json if necessary
        parsed_content = (
            json.loads(dsstox.content) if type(dsstox.content) is str else dsstox.content
        )

        content = {
            k: parsed_content[k]
            for k in ("preferredName", "casrn", "dtxsid", "smiles", "molWeight")
        }
        content["url_dashboard"] = dsstox.get_dashboard_url()

        # get image
        url = dsstox.get_image_url()
        response = requests.get(url)
        content["image"] = base64.b64encode(response.content).decode("utf-8")

        # call it a success if we made it here
        d["status"] = "success"
        d["content"] = content

    except AttributeError:
        logger.error(f"Request failed: {response.text}", exc_info=True)

    except Exception as e:
        logger.error(str(e), exc_info=True)

    return d
