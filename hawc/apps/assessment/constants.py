from django.db import models


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


class AssessmentType(models.TextChoices):
    IRIS = "IRIS", "IRIS"
    PPRTV = "PPRTV", "PPRTV"
    TSCA = "TSCA", "TSCA"
    RE = "RE", "RE"
    OW_HESD = "OW HESD", "OW HESD"
    OTHER = "Other", "Other"


class Milestone(models.TextChoices):
    SCOPING = "Scoping", "Scoping"
    PROBLEM_FORM = "Problem Formulation", "Problem Formulation"
    INTERNAL_R = "Internal Review", "Internal Review"
    INTERAGENCY_R = "Interagency Review", "Interagency Review"
    PUBLIC_COMMENT = "Public Comment", "Public Comment"
    EXTERNAL_PR = "External Peer Review", "External Peer Review"
    FINAL = "Final", "Final"


class PRType(models.TextChoices):
    CONTRACT = "CL", "Contract-Led"
    FACA = "FACA", "FACA Panel"
    NASEM = "NASEM", "NASEM"
    JOURNAL = "JR", "Journal Review"
    NONE = "NONE", "No Review"


class EvaluationType(models.TextChoices):
    CANCER = "CANCER", "Cancer"
    NONCANCER = "NONCANCER", "Noncancer"
    BOTH = "BOTH", "Cancer and Noncancer"


class ValueType(models.TextChoices):
    SCREEN_RFD = "Screening-Level RfD", "Screening-Level RfD"
    SCREEN_RFC = "Screening-Level RfC", "Screening-Level RfC"
    ORGAN_RFD = "Organ-Specific RfD", "Organ-Specific RfD"
    ORGAN_RFC = "Organ-Specific RfC", "Organ-Specific RfC"
    OVERALL_RFD = "Overall RfD", "Overall RfD"
    OVERALL_RFC = "Overall RfC", "Overall RfC"
    IUR = "IUR", "IUR"
    OSF = "OSF", "OSF"
    NONE = "No Value", "No Value"
    OTHER = "Other", "Other"


class Confidence(models.TextChoices):
    HIGH = "HI", "High"
    MEDIUM = "MED", "Medium"
    LOW = "LOW", "Low"


def default_metadata() -> dict[str, str]:
    return dict(key="value")
