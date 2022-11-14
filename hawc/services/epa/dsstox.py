import logging
import re
from typing import NamedTuple

import requests

logger = logging.getLogger(__name__)


RE_DTXSID = r"DTXSID\d+"


class DssSubstance(NamedTuple):
    dtxsid: str
    content: dict

    @classmethod
    def create_from_dtxsid(cls, dtxsid: str) -> "DssSubstance":
        """Fetch a DssTox instance from the actor webservices using a DTXSID.

        Args:
            dtxsid (str): a DTXSID identifier

        Raises:
            ValueError: if object could not be created

        Returns:
            DssSubstance: a substance
        """
        if not re.compile(RE_DTXSID).fullmatch(dtxsid):
            raise ValueError(f"Invalid DTXSID: {dtxsid}")

        response = requests.get(
            f"https://comptox.epa.gov/dashboard-api/ccdapp2/chemical-detail/search/by-dsstoxsid?id={dtxsid}"
        )
        response_dict = response.json()
        if response_dict == [] or response_dict["dsstoxSubstanceId"] != dtxsid:
            raise ValueError(f"{dtxsid} not found in DSSTox lookup")

        response_dict["dtxsid"] = response_dict.pop("dsstoxSubstanceId")
        response_dict.pop("presenceInLists")
        obj = cls(dtxsid=response_dict["dtxsid"], content=response_dict)

        return obj
