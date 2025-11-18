from django.db import models

from ..common.constants import NA, NR

class PlaceholderChoices(models.IntegerChoices):
    FAKE = 0, "Not Set"
    DUH = 1, "Fake"

class PecoType(models.TextChoices):
    PE = "PE", "PECO (supplemental)"
    NO = "NO", "No (off-PECO)"
    UN = "UN", "Uncertain of PECO relevance"


class PecoSupplementalType(models.TextChoices):
    LE = "LE", "Letter to/from editor or commentary"
    CO = "CO", "Conference proceeding or abstract"
    RE = "RE", "Remediation/spill/improper disposal"
    SE = "SE", "Only secondary quantitative data"
    QU = "QU", "Only qualitative contextual information or concentrations in rocks"
    IS = "IS", "Isomer only (not applicable to asbestos)"


class StudyType(models.TextChoices):
	MON = "MON", "Monitoring"
	MDI = "MDI", "Modeling - dose/intake"
	MPC = "MPC", "Modeling - predicted concentration"
	XWF = "XWF", "Experimental  - weight fraction or concentration in consumer product"
	EXP = "EXP", "Experimental"
	SUR = "SUR", "Survey"
	DAT = "DAT", "Database"
	COM = "COM", "Completed Assessment"
	EPI = "EPI", "Epi"

class ConsumerProdDermalFlux(models.TextChoices):
    CP = "CP", "Consumer products/articles (e.g. weight fractions or use instructions like dilution rate, application rate, application methods, amount of product per use, etc.)"
    DE = "DE", "Dermal parameters (e.g. dermal absorption fraction, neat and aqueous Kp, skin permeability coefficient, skin permeation coefficient, skin permeation, and skin absorption)"
    FL = "FL", "Fluxes (e.g. chemical fluxes in surface water with units mass per area per time)"


class ChemicalInventoryItemType(models.TextChoices):
    CTE = "CTE", "Chemical to extract (TSCA, targeted metabolite, PAD)"
    NTC = "NTC", "ONLY non-targeted chemical that will not be extracted (isomer, siloxane structure of D4, degradant of D4, precursor, or metabolite)"


# do we want this defined in db instead of in code?
class TSCAChemicalSubstance(models.TextChoices):
	ODCB = "ODCB", "o-Dichlorobenzene (o-DCB or 1,2 DCB) (ODCB)"
	PDCB = "PDCB", "p-Dichlorobenzene (p-DCB or 1,4 DCB) (PDCB)"
	EDC = "EDC", "1,2-Dichloroethane (EDC)"
	TDCE = "TDCE", "trans-1,2-Dichloroethylene (TDCE)"
	TCA = "TCA", "1,1,2-Trichloroethane (TCA)"
	DCP = "DCP", "1,2-Dichloropropane  (DCP)"
	DCE = "DCE", "1,1-Dichloroethane (DCE)"
	TPP = "TPP", "Triphenyl Phosphate (TPP) (Phosphoric acid, triphenyl ester)"
	TBBPA = "TBBPA", "Tetrabromobisphenol A (TBBPA)"
	TCEP = "TCEP", "Tris(2-chloroethyl) phosphate (TCEP)"
	EDB = "EDB", "Ethylene Dibromide (EDB)"
	BTD = "BTD", "1,3-Butadiene (BTD)"
	PAD = "PAD", "Phthalic Anhydride (PAD)"
	HHCB = "HHCB", "HHCB (Galaxolide)"
	FDH = "FDH", "Formaldehyde (FDH)"
	DBP = "DBP", "Dibutyl Phthalate (DBP)"
	BBP = "BBP", "Butyl benzyl Phthalate (BBP)"
	DEHP = "DEHP", "Di-ethylhexyl Phthalate (DEHP)"
	DIBP = "DIBP", "Di-isobutyl Phthalate (DIBP)"
	DCHP = "DCHP", "Dicyclohexyl Phthalate (DCHP)"
	DIDP = "DIDP", "Di-isodecyl Phthlate (DIDP)"
	DINP = "DINP", "Di-isononyl Phthlate (DINP)"
	D4 = "D4", "D4"

class ChemicalForm(models.TextChoices):
    PAR = "PAR", "Parent/TSCA Chemical"
    MET = "MET", "Targeted Metabolite / Degradant (D4 or PAD)"

# again, do we want this in db instead?
class TargetedMetaboliteOrDegradant(models.TextChoices):
	BCEP = "BCEP", "BCEP (Bis(2-chloroethyl)phosphate) [TCEP - Human biomonitoring]"
	DPHP = "DPHP", "DPHP (Di(2-propylheptyl) phthalate) [TPP - Human biomonitoring]"
	TPHPM1 = "TPHP-M1", "TPHP-M1 (Hydroxyphenyl phenyl phosphate) [TPP - Human biomonitoring]"
	HEMA = "HEMA", "HEMA (S-(hydroxyethyl)mercapturic acid) [EDB - Human biomonitoring]"
	TDA = "TDA", "TDA (thiodiacetic acid) [EDB - Human biomonitoring]"
	SODA = "SODA", "SODA (thiodiacetic acid sulfoxide) [EDB - Human biomonitoring]"
	PA = "PA", "PA (Phthalic acid) [PAD - urine]"
	MEHHP = "MEHHP", "MEHHP (Mono-(2-ethyl-5-hydroxyhexyl) phthalate, (5OH-MEHP), OH-MEHP) [DEHP - urine]"
	MEOHP = "MEOHP", "MEOHP (Mono-(2-ethyl-5-oxohexyl) phthalate, oxo-MEHP, (5oxo-MEHP)) [DEHP - urine]"
	MEHP = "MEHP", "MEHP (Mono-(2-ethyl)-hexyl phthalate) [DEHP - urine]"
	MECPP = "MECPP", "MECPP (Mono-(2-ethyl-5-carboxypentyl) phthalate, (5cx-MEPP), cx-MEPP) [DEHP - urine]"
	MBP = "MBP", "MBP (Monobutyl phthalate) [DBP or DnBP - urine]"
	MHBP = "MHBP", "MHBP (Mono-3-hydroxy-n-butyl phthalate) [DBP or DnBP - urine]"
	MNBP = "MnBP", "MnBP (Mono-n-butyl phthalate) [DBP or DnBP - urine]"
	MINP = "MiNP", "MiNP (Mono-isononyl phthalate, MNP) [DNP or DiNP - urine, breastmilk, maternal or infant blood]"
	MCOP = "MCOP", "MCOP (Mono-(carboxyisooctyl) phthalate, MCiOP) [DNP or DiNP - urine, breastmilk, maternal or infant blood]"
	MONP = "MONP", "MONP (Mono-oxoisononyl phthalate, 7 oxo-MMeOp, MOiNP, 7-oxo-MiNP, oxo-MiNP) [DNP or DiNP - urine, breastmilk, maternal or infant blood]"
	OHMINP = "OH-MiNP", "OH-MiNP (Mono(hydroxyisononyl) phthalate, MHiNP) [DNP or DiNP - urine, breastmilk, maternal or infant blood]"
	MIBP = "MiBP", "MiBP (Mono-isobutyl phthalate) [DiBP - urine]"
	MHIBP = "MHiBP", "MHiBP (Mono-2-methyl-2-hydroxypropyl phthalate) [DiBP - urine]"
	MCNP = "MCNP", "MCNP (Mono-(carboxynonyl) phthalate) [DiDP - urine, breastmilk, maternal or infant blood]"
	MBZP = "MBzP", "MBzP (Mono-benzyl phthalate) [BBP or BzBP - urine]"
	MCHP = "MCHP", "MCHP (Monocyclohexyl phthalate) [DCH or DCHP - urine]"

class GeographicSetting(models.TextChoices):
	UR = "UR", "Urban"
	SU = "SU", "Suburban"
	RU = "RU", "Rural"
	IN = "IN", "Industrial"
	AG = "AG", "Agricultural"
	RE = "RE", "Remote"
	PO = "PO", "Port"
	MA = "MA", "Marine"
	OT = "OT", "Other"
	NR = "NR", "Not Reported/Unknown"

"""
class VarianceType(models.IntegerChoices):
    NA = 0, NA
    SD = 1, "SD"
    SE = 2, "SE"
    SEM = 3, "SEM"
    GSD = 4, "GSD"
    IQR = 5, "IQR (interquartile range)"
    OT = 6, "other"
"""


