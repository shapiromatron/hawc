from enum import Enum


class HawcGroups(Enum):
    BETA_TESTER = "beta tester"
    REQUIRES_2FA = "2fa-required"
    CAN_CREATE_ASSESSMENTS = "can-create-assessments"
