import logging
import re
from typing import Dict, NamedTuple

import requests

logger = logging.getLogger(__name__)


RE_DTXSID = r"DTXSID\d+"


class DssSubstance(NamedTuple):
    dtxsid: str
    content: Dict

    @staticmethod
    def get_url(id_: str) -> str:
        return f"https://actorws.epa.gov/actorws/chemIdentifier/v01/resolve.json?identifier={id_}"

    @classmethod
    def create_from_dtxsid(cls, dtxsid: str) -> "DssSubstance":
        """Fetch a DssTox instance from the actor webservices using a DTXSID.

        Args:
            dtxsid (str): a DTXSID identifer

        Raises:
            ValueError: if object could not be created

        Returns:
            DssSubstance: a substance
        """
        if not re.compile(RE_DTXSID).fullmatch(dtxsid):
            raise ValueError(f"Invalid DTXSID: {dtxsid}")

        # obj = cls.create_from_identifier(dtxsid)
        response = requests.get(
            f"https://comptox.epa.gov/dashboard-api/ccdapp2/chemical-detail/search/by-dsstoxsid?id={dtxsid}"
        )
        response_dict = response.json()
        response_dict["dtxsid"] = response_dict.pop("dsstoxSubstanceId")
        response_dict.pop("presenceInLists")
        obj = cls(dtxsid=response_dict["dtxsid"], content=response_dict)

        if obj.dtxsid != dtxsid:
            raise ValueError(f"{dtxsid} not found in DSSTox lookup")

        return obj

    @classmethod
    def create_from_identifier(cls, id_: str) -> "DssSubstance":
        """Fetch a DssTox instance from the actor webservices using an identifier.

        Args:
            id_ (str): a chemical identifer (DTXSID, CASRN, common name, etc)

        Raises:
            ValueError: if object could not be created

        Returns:
            DssSubstance: a substance
        """
        url = cls.get_url(id_)
        response = requests.get(url)
        response_dict = response.json()["DataRow"]

        dtxsid = response_dict["dtxsid"]
        if not dtxsid:
            raise ValueError(f"Chemical identifier {id_} not found in DSSTox lookup")

        return cls(dtxsid=dtxsid, content=response_dict)
