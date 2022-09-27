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


class Status(models.IntegerChoices):
    SCOPING = 0, "Scoping"
    PROBLEM_FORM = 5, "Problem Formulation"
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
    NONE = 20, "No Review"


class EvaluationType(models.IntegerChoices):
    CANCER = 0, "Cancer"
    NONCANCER = 1, "Noncancer"
    BOTH = 2, "Cancer and Noncancer"


class ValueType(models.IntegerChoices):
    SCREEN_RFD = 0, "Screening-Level RfD"
    SCREEN_RFC = 5, "Screening-Level RfC"
    ORGAN_RFD = 10, "Organ-Specific RfD"
    ORGAN_RFC = 15, "Organ-Specific RfC"
    OVERALL_RFD = 20, "Overall RfD"
    OVERALL_RFC = 25, "Overall RfC"
    IUR = 30, "IUR"
    OSF = 35, "OSF"
    OTHER = 45, "Other"


class Confidence(models.IntegerChoices):
    HIGH = 30, "High"
    MEDIUM = 20, "Medium"
    LOW = 10, "Low"
    NA = 0, "Not Applicable"
