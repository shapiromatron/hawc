from django.db import models


class SimpleYesNo(models.TextChoices):
    YES = "YES", "Yes"
    NO = "NO", "No"


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


class ControlsUsed(models.TextChoices):
    YS = "YS", "yes"
    NO = "NO", "no"
    NS = "NS", "not specified"
    NR = "NR", "not required"


class ControlType(models.TextChoices):
    UNT = "UNT", "untreated control"
    POS = "POS", "positive control item"
    REF = "REF", "reference item"
    SVC = "SVC", "solvent / vehicle control"
    NEG = "NEG", "negative control item"
    OTH = "OTH", "other"


class YesNoRemarks(models.TextChoices):
    YS = "YS", "Yes, with remarks"
    NO = "NO", "no"
    NR = "NR", "not relevant"
    UN = "UN", "unknown"


class EndpointProcess(models.TextChoices):
    APOP = "APOP", "apoptotic process - [GO:0008219]"
    BIOP = "BIOP", "biosynthetic process - [GO:0009058]"
    CATA = "CATA", "catalytic activity - [GO:0003824]"
    CACT = "CACT", "cell activation - [GO:0001775]"
    CDEA = "CDEA", "cell death - [GO:0008219]"
    CDIF = "CDIF", "cell differentiation - [GO:0030154]"
    CMIG = "CMIG", "cell migration - [GO:0016477]"
    CPRO = "CPRO", "cell proliferation - [GO:0008283]"
    GEXP = "GEXP", "gene expression - [GO:0010467]"
    KACT = "KACT", "keratinocyte activation - [GO:0032980]"
    METP = "METP", "metabolic process - [GO:0008152]"
    NURA = "NURA", "nuclear receptor activity - [GO:0004879]"
    NURB = "NURB", "nuclear receptor binding - [GO:0016922]"
    OXST = "OXST", "oxidative stress - [NCIT:C17741]"
    PERA = "PERA", "peroxidase activity - [GO:0004601]"
    PNCD = "PNCD", "programmed necrotic cell death - [GO:0097300]"
    PROB = "PROB", "protein binding - [GO:0005515]"
    PROI = "PROI", "protein iodination - [GO:0018077]"
    RECA = "RECA", "receptor activity - [GO:0004872]"
    RECB = "RECB", "receptor binding - [GO:0005102]"
    SIGN = "SIGN", "signalling - [GO:0023052]"
    SHBP = "SHBP", "steroid hormone biosynthetic process - [GO:0120178]"
    TRAA = "TRAA", "transporter activity - [GO:0005215]"
    OTHR = "OTHR", "other"


class EndpointObject(models.TextChoices):
    NAME = "NAME", "Object name, specify"
    IDEN = "IDEN", "Object identifier, specify"


class EndpointAction(models.TextChoices):
    ALTR = "ALTR", "alteration"
    BIND = "BIND", "binder / non-binder"
    DECR = "DECR", "decrease"
    DECA = "DECA", "decrease, antagonism"
    DISR = "DISR", "disruption"
    DREG = "DREG", "down regulation"
    ENHA = "ENHA", "enhancement"
    INCR = "INCR", "increase"
    INDE = "INDE", "increase / decrease"
    INCA = "INCA", "increase, agonism"
    INDU = "INDU", "induction"
    INHI = "INHI", "inhibition"
    OCCR = "OCCR", "occurrence"
    UREG = "UREG", "up regulation"
    OTHR = "OTHR", "other"
