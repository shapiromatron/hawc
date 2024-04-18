from django.db import models

from .permissions import AssessmentPermissions

ADAF_FOOTNOTE = (
    "Age-dependent ajustment factors (ADAFs) have not been applied to the value shown. "
    "Application of ADAFs is recommended in combination with appropriate exposure data when "
    "assessing risk associated with early-life exposure. More information is available in the "
    "comments field for this value."
)


class AssessmentRole(models.TextChoices):
    PROJECT_MANAGER = "Project Manager"
    TEAM_MEMBER = "Team Member"
    REVIEWER = "Reviewer"
    NO_ROLE = "No Role"


class PublishedStatus(models.TextChoices):
    PUBLIC = "Public"
    UNLISTED = "Unlisted"
    PRIVATE = "Private"


class AssessmentViewPermissions(models.IntegerChoices):
    PROJECT_MANAGER = 1
    TEAM_MEMBER = 2
    VIEWER = 3


class AssessmentViewSetPermissions(models.IntegerChoices):
    CAN_VIEW_OBJECT = 1
    CAN_EDIT_OBJECT = 2
    CAN_EDIT_ASSESSMENT = 3
    TEAM_MEMBER_OR_HIGHER = 4
    PROJECT_MANAGER_OR_HIGHER = 5

    def has_permission(self, assessment, user, **kwargs):
        perms = AssessmentPermissions.get(assessment)
        return getattr(perms, self.name.lower())(user, **kwargs)


class NoelName(models.IntegerChoices):
    NEL = 2, "NEL/LEL"
    NOEL = 0, "NOEL/LOEL"
    NOAEL = 1, "NOAEL/LOAEL"


class RobName(models.IntegerChoices):
    ROB = 0, "Risk of bias"
    SE = 1, "Study evaluation"


class JobStatus(models.IntegerChoices):
    PENDING = 1, "PENDING"
    SUCCESS = 2, "SUCCESS"
    FAILURE = 3, "FAILURE"


class JobType(models.IntegerChoices):
    TEST = 1, "TEST"


class EpiVersion(models.IntegerChoices):
    V1 = 1, "v1"
    V2 = 2, "v2"


class Status(models.IntegerChoices):
    SCOPING = 0, "Scoping"
    PROBLEM_FORM = 5, "Problem Formulation"
    PROTOCOL = 8, "Protocol"
    INTERNAL_REVIEW = 10, "Internal Review"
    INTERAGENCY_REVIEW = 15, "Interagency Review"
    PUBLIC_COMMENT = 20, "Public Comment"
    EXTERNAL_REVIEW = 25, "External Peer Review"
    FINAL = 30, "Final"
    Other = 35, "Other"


class PeerReviewType(models.IntegerChoices):
    CONTRACT = 0, "Contract-Led"
    FACA = 5, "FACA Panel"
    NASEM = 10, "NASEM"
    JOURNAL = 15, "Journal Review"
    OTHER = 18, "Other"
    NONE = 20, "No Review"
    NA = 25, "Not Applicable"

    def display(self) -> bool:
        hidden = self in [self.NONE, self.OTHER, self.NA]
        return not hidden


class EvaluationType(models.IntegerChoices):
    CANCER = 0, "Cancer"
    NONCANCER = 1, "Noncancer"
    BOTH = 2, "Cancer and Noncancer"


class ValueType(models.IntegerChoices):
    OVERALL_RFD = 0, "Overall RfD"
    OVERALL_RFC = 10, "Overall RfC"
    IUR = 20, "IUR"
    OSF = 30, "OSF"
    SCREEN_RFD = 40, "Screening-Level RfD"
    SCREEN_RFC = 50, "Screening-Level RfC"
    ORGAN_RFD = 60, "Organ-Specific RfD"
    ORGAN_RFC = 70, "Organ-Specific RfC"
    OTHER = 100, "Other"


class Confidence(models.IntegerChoices):
    HIGH = 30, "High"
    MEDIUM = 20, "Medium"
    LOW = 10, "Low"
    NA = 0, "Not Applicable"


class UncertaintyChoices(models.IntegerChoices):
    ONE = 1, "1"
    THREE = 3, "3"
    TEN = 10, "10"
    THIRTY = 30, "30"
    ONE_HUNDRED = 100, "100"
    THREE_HUNDRED = 300, "300"
    ONE_THOUSAND = 1_000, "1,000"
    THREE_THOUSAND = 3_000, "3,000"
    TEN_THOUSAND = 10_000, "10,000"
    THIRTY_THOUSAND = 30_000, "30,000"
    ONE_HUNDRED_THOUSAND = 100_000, "100,000"
    THREE_HUNDRED_THOUSAND = 300_000, "300,000"
