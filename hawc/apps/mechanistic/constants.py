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


class EndpointDetails(models.TextChoices):
    SEMI = "SEMI", "Semi or non-quantitative detection methods"
    QUAN = "QUAN", "quantitative"



class EndpointDetectionMethod(models.TextChoices):
    ANALYTICAL = "ANALYTICAL", "analytical method (e.g. LC/MS)"
    CHROMATO = "CHROMATO", "chromatography"
    COMPLEX = "COMPLEX", "complex detection methods (e.g. imaging)"
    FLUORO = "FLUORO", "fluorescence"
    LUMIN = "LUMIN", "luminescence"
    RADIOACTIV = "RADIOACTIV", "radioactivity"
    ABSORP = "ABSORP", "UV/VIS absorption"
    OTHER = "OTHER", "other"

class EndpointParameters(models.TextChoices):
	RFU = "RFU", "RFU"
	RLU = "RLU", "RLU"
	OD = "OD", "OD"
	CPD = "CPD", "Detected compound (e.g. metabolite detection with LC-MS)"
	PKA = "PKA", "Peak area"
	PKH = "PKH", "Peak height"
	FSC = "FSC", "Forward Scatter"
	SSC = "SSC", "Side Scatter"
	DBI = "DBI", "Detected biomarker (e.g. with imaging)"
	OTH = "OTH", "Other"

class VehicleSolventType(models.TextChoices):
    DMSO = "DMSO", "DMSO"
    ACET = "ACET", "acetone"
    ETHA = "ETHA", "ethanol"
    NREQ = "NREQ", "not required"
    NSPE = "NSPE", "not specified"
    SALI = "SALI", "saline"
    TREX = "TREX", "treatment/exposure medium"
    WATR = "WATR", "water"
    OTHR = "OTHR", "other"


class VehicleSolventConcentrationAmount(models.TextChoices):
    PT1 = "PT1", "0.1%"
    PT2 = "PT2", "0.2%"
    PT5 = "PT5", "0.5%"
    ONE = "ONE", "1.0%"
    NS = "NS", "Not specified"
    OTH = "OTH", "Other, please specify"


class ConcentrationSelection(models.TextChoices):
	HUEX = "HUEX", "human exposure levels"
	INDE = "INDE", "interference with the detection method (e.g. auto fluorescence)"
	INTS = "INTS", "interference with the test system (e.g. cytotoxicity or pH)"
	PRIN = "PRIN", "prior information of response (e.g. dose-range finding experiment)"
	SOEM = "SOEM", "solubility in exposure medium"
	SOSO = "SOSO", "solubility in solvent"
	UNKW = "UNKW", "unknown"
	OTHR = "OTHR", "other"

class VehicleSolventConcentrationUnit(models.TextChoices):
    TODO = "TODO", "todo/placeholder"

class ConcentrationUnits(models.TextChoices):
	PCT = "PCT", "%"
	GKG = "GKG", "g/kg"
	M = "M", "M"
	GL = "GL", "g/L"
	PPB = "PPB", "ppb"
	PPM = "PPM", "ppm"
	OTH = "OTH", "other"
