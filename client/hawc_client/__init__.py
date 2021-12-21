from .animal import AnimalClient
from .assessment import AssessmentClient
from .base_client import BaseClient
from .epi import EpiClient
from .epimeta import EpiMetaClient
from .hawc_session import HawcSession
from .invitro import InvitroClient
from .literature import LiteratureClient
from .riskofbias import RiskOfBiasClient
from .study import StudyClient
from .summary import SummaryClient
from .vocab import VocabClient

__version__ = "2020.10"
__all__ = ["HawcClient"]


class HawcClient(BaseClient):
    """
    HAWC Client.

    Usage:
        client = HawcClient("https://hawcproject.org")
        # If authentication is needed...
        client.authenticate("username","password")
        # To make requests...
        client.<namespace>.<method>()

    Below are the available namespaces:
        animal, epi, epimeta, invitro, lit, riskofbias, summary
    """

    def __init__(self, root_url: str = "https://hawcproject.org"):
        super().__init__(HawcSession(root_url))

        self.animal = AnimalClient(self.session)
        self.assessment = AssessmentClient(self.session)
        self.epi = EpiClient(self.session)
        self.epimeta = EpiMetaClient(self.session)
        self.invitro = InvitroClient(self.session)
        self.lit = LiteratureClient(self.session)
        self.riskofbias = RiskOfBiasClient(self.session)
        self.summary = SummaryClient(self.session)
        self.study = StudyClient(self.session)
        self.vocab = VocabClient(self.session)

    def authenticate(self, email: str, password: str):
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        self.session.authenticate(email, password)
