import logging
import re
from typing import Dict, NamedTuple

import requests

logger = logging.getLogger(__name__)


RE_DTXSID = r"DTXSID\d+"


class DssSubstance(NamedTuple):
    dtxsid: str
    content: Dict

    @classmethod
    def create(cls, dtxsid: str) -> "DssSubstance":
        """Fetch a DssTox instance from the actor webservices

        Args:
            dtxsid (str): a DTXSID identifer

        Raises:
            ValueError: if object could not be created

        Returns:
            DssSubstance: a substance
        """

        if not re.compile(RE_DTXSID).fullmatch(dtxsid):
            raise ValueError(f"Invalid DTXSID: {dtxsid}")

        url = f"https://actorws.epa.gov/actorws/chemIdentifier/v01/resolve.json?identifier={dtxsid}"
        response = requests.get(url)
        response_dict = response.json()["DataRow"]

        if not response_dict["dtxsid"]:
            raise ValueError(f"Chemical identifier '{dtxsid}' not found on DSSTox lookup.")

        if response_dict["dtxsid"] != dtxsid:
            raise ValueError(f"DTXSID '{dtxsid}' not found on DSSTox lookup.")

        return cls(dtxsid=dtxsid, content=response_dict)
