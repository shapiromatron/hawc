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
    IRIS = "IRIS"
    PPRTV = "PPRTV"
    TSCA = "TSCA"
    RE = "RE"
    OW_HESD = "OW HESD"
    OTHER = "Other"


class Milestone(models.TextChoices):
    SCOPING = "Scoping"
    PROBLEM_FORM = "Problem Formulation"
    INTERNAL_R = "Internal Review"
    INTERAGENCY_R = "Interagency Review"
    PUBLIC_COMMENT = "Public Comment"
    EXTERNAL_PR = "External Peer Review"
    FINAL = "Final"


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
    SCREEN_RFD = "SCREEN_RFD", "Screening-Level RfD"
    SCREEN_RFC = "SCREEN_RFC", "Screening-Level RfC"
    ORGAN_RFD = "ORGAN_RFD", "Organ-Specific RfD"
    ORGAN_RFC = "ORGAN_RFC", "Organ-Specific RfC"
    OVERALL_RFD = "OVERALL_RFD", "Overall RfD"
    OVERALL_RFC = "OVERALL_RFC", "Overall RfC"
    IUR = "IUR", "IUR"
    OSF = "OSF", "OSF"
    NONE = "NONE", "No Value"


class Confidence(models.TextChoices):
    HIGH = "HI", "High"
    MEDIUM = "MED", "Medium"
    LOW = "LOW", "Low"
