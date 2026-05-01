from django.db import models


class ExperimentGuideline(models.TextChoices):
    YES = "YES", "Yes"
    NO = "NO", "No"
    NR = "NR", "Not reported"


class CompositionPurity(models.TextChoices):
    AG = "AG", "Analytical Grade"
    TG = "TG", "Technical Grade"
    NS = "NS", "Purity Not Specified"
    NA = "NA", "Not Applicable (e.g. In Silico Study)"
    OT = "OT", "Other"


class TestSystemType(models.TextChoices):
    BAC = "BAC", "bacteria"
    CFR = "CFR", "cellular fraction"
    BTS = "BTS", "complex biological test system"
    CLN = "CLN", "cell line"
    PCB = "PCB", "physical / chemical based"
    PRI = "PRI", "primary cells"
    TIS = "TIS", "tissue"
    YEA = "YEA", "yeast"
    CF = "CF", "cell free"
    OTH = "OTH", "other, specify"


class TestSystemSupplier(models.TextChoices):
    CO = "CO", "Commercial supplier, specify"
    NC = "NC", "Non-commercial supplier, specify"
    IH = "IH", "In house developed, specify"
    OT = "OT", "Other"


class GeneticModification(models.TextChoices):
    POSTPURCHASE = "POSTPURCHASE", "genetically modified after purchase, prior to use"
    SUPPLIER = "SUPPLIER", "genetically modified by supplier"
    NA = "NA", "not applicable"
    NOMOD = "NOMOD", "not genetically modified"
    NS = "NS", "not specified"


class MetabolicCompetence(models.TextChoices):
    LIM = "LIM", "limited metabolic activity, specify"
    MET = "MET", "metabolic activity, specify"
    UNK = "UNK", "unknown metabolic activity"
    OTH = "OTH", "other information on metabolic competence, describe:"
    NA = "NA", "not applicable"


class TestSystemQualityControl(models.TextChoices):
    ABSMYC = "ABSMYC", "absence of mycoplasma"
    STERILITY = "STERILITY", "sterility (absence of bacteria, fungi, yeast)"
    ABSPATH = "ABSPATH", "absence of pathological viruses"
    KARYO = "KARYO", "karyotype stability"
    RESPPOS = "RESPPOS", "test system response to positive control"
    RESPSOLV = "RESPSOLV", "test system response to solvent control"
    RESPBASE = "RESPBASE", "test system baseline response"
    EXPBIO = "EXPBIO", "test system expression of biological markers"
    OTHER = "OTHER", "Other, specify"
