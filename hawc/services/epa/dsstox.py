import logging
import re
from typing import NamedTuple, Self

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


RE_DTXSID = r"DTXSID\d+"


class DssSubstance(NamedTuple):
    dtxsid: str
    content: dict

    @classmethod
    def create_from_dtxsid(cls, dtxsid: str) -> Self:
        """Fetch a DssTox instance from the actor webservices using a DTXSID.

        Args:
            dtxsid (str): a DTXSID identifier

        Raises:
            ValueError: if object could not be created

        Returns:
            DssSubstance: a substance
        """
        if settings.HAWC_FEATURES.FAKE_IMPORTS:
            return cls(
                dtxsid="DTXSID6026296",
                content={
                    "id": "FD70373DEB12FD6675FDFD64FDFDFD0E3AFD53FD74784AFD5AFD1136FD",
                    "casrn": "7732-18-5",
                    "compoundId": 6296,
                    "preferredName": "Water",
                    "molFormula": "H2O",
                    "hasStructureImage": 1,
                    "averageMass": 18.015,
                    "dtxsid": "DTXSID6026296",
                    "dtxcid": "DTXCID106296",
                },
            )
        if not re.compile(RE_DTXSID).fullmatch(dtxsid):
            raise ValueError(f"Invalid DTXSID: {dtxsid}")
        if settings.CCTE_API_KEY is None and settings.IS_TESTING is False:
            raise ValueError("Missing API key")
        response = requests.get(
            f"https://api-ccte.epa.gov/chemical/detail/search/by-dtxsid/{dtxsid}",
            headers={"x-api-key": settings.CCTE_API_KEY, "Content-Type": "application/json"},
        )
        response_dict = response.json()
        if response_dict.get("dtxsid") != dtxsid:
            raise ValueError(f"{dtxsid} not found in DSSTox lookup")
        return cls(dtxsid=response_dict["dtxsid"], content=response_dict)
