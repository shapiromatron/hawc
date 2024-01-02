"""A client for the Health Assessment Workspace Collaborative (HAWC)."""

from .animal import AnimalClient
from .assessment import AssessmentClient
from .client import BaseClient, InteractiveHawcClient
from .epi import EpiClient
from .epimeta import EpiMetaClient
from .epiv2 import EpiV2Client
from .exceptions import HawcClientException, HawcServerException
from .invitro import InvitroClient
from .literature import LiteratureClient
from .riskofbias import RiskOfBiasClient
from .session import HawcSession
from .study import StudyClient
from .summary import SummaryClient
from .vocab import VocabClient

__version__ = "2023.2"
__all__ = [
    "BaseClient",
    "HawcClient",
    "HawcClientException",
    "HawcServerException",
    "InteractiveHawcClient",
]


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
        self.epiv2 = EpiV2Client(self.session)
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

    def set_authentication_token(self, token: str, login: bool = False) -> bool:
        """
        Set authentication token for hawc client session.

        Args:
            token (str): authentication token from your user profile
            login (bool, default False): if True, creates a django cookie-based session for HAWC
                similar to a standard web-browser. If False (default), creates a token-
                based django session for using the API. Requests using cookie-based sessions
                require CSRF tokens, so form functionality will be limited.

        Returns
            bool: Returns true if session is valid
        """
        return self.session.set_authentication_token(token, login)
