from django.db import models

# Metadata
class StudyType(models.IntegerChoices):

    OBS = 0, "Observational/gradient"
    MAN = 1, "Manipulation/experiment"
    SIM = 2, "Simulation"
    MET = 3, "Meta-analysis"
    REV = 4, "Review"


class StudySetting(models.IntegerChoices):
    FIELD = 0, "Field"
    MESO = 1, "Mesocosm"
    GREEN = 2, "Greenhouse"
    LAB = 3, "Laboratory"
    MOD = 4, "Model"
    NA = 5, "Not Applicable"


class HabitatType(
    models.IntegerChoices
):  # figure out how to use this to filter following habitat type fields
    TERR = 0, "Terrestrial"
    RIP = 1, "Riparian"
    FRESH = 2, "Freshwater aquatic"
    ESTU = 3, "Estuarine"
    MAR = 4, "Marine"


class TerrestrialHab(models.IntegerChoices):
    FOR = 0, "Forest"
    GRASS = 1, "Grassland"
    DES = 2, "Desert"
    HEATH = 3, "Heathland"
    AG = 4, "Agricultural"
    URB = 5, "Urban/suburban"
    TUND = 6, "Tundra"


class AquaticHab(models.IntegerChoices):
    STREAM = 0, "Stream/river"
    WETL = 1, "Wetland"
    LAKE = 2, "Lake/reservoir"
    ART = 3, "Artificial"


# Cause
class BioOrg(models.IntegerChoices):  # to be used in both cause and effect tables
    ECOS = 0, "Ecosystem"
    COMM = 1, "Community"
    POP = 2, "Population"
    IND = 3, "Individual organism"
    SUB = 4, "Sub-organismal"


class EcoVocabCategories(models.IntegerChoices):
    TERM = 0, "Term"
    MEASURE = 1, "Measure"
    MTF = 2, "Measure type filter"
    MT = 3, "Measure type"


class CauseTerm(
    models.IntegerChoices
):  # does caroline have an updated list, or does this need to be a fixture??
    TBD = 0, "TBD"
    WAT = 1, "Water Quality"


class CauseMeasure(
    models.IntegerChoices
):  # does caroline have an updated list, or does this need to be a fixture??
    TBD = 0, "TBD"
    NUT = 1, "Nutrients"


class CauseTrajectory(models.IntegerChoices):
    INCR = 0, "Increase"
    DECR = 1, "Decrease"
    CHANGE = 2, "Change"
    OTHER = 3, "Other"


# Effect
class EffectTerm(models.IntegerChoices):  # should this be a fixture?
    TBD = 0, "TBD"
    ALGAE = 1, "Algae"


class EffectMeasure(models.IntegerChoices):
    TBD = 0, "TBD"
    ABUND = 1, "Abundance"


class EffectTrajectory(models.IntegerChoices):
    INCR = 0, "Increase"
    DECR = 1, "Decrease"
    CHANGE = 2, "Change"
    NOCHANGE = 3, "No change"
    OTHER = 4, "Other"


class Sort(models.IntegerChoices):
    TBD = 0, "TBD"


class MeasureTypeFilter(models.IntegerChoices):
    CORR = 0, "Correlation coefficient"
    RSQ = 1, "R-squared"
    MEANDIFF = 2, "Mean difference"
    ANOVA = 3, "ANOVA/PERMANOVA"
    RATIO = 4, "Ratio"
    BETA = 5, "Slope coefficient (beta)"
    ORD = 6, "Ordination"
    THRESH = 7, "Threshold"


class EcoVocabChoices(models.Model):
    class MeasureType(
        models.IntegerChoices
    ):  # make this an autocomplete thing - use same EcoVocab table as above to do the filtering
        # correlation coefficient:
        PEARSON = 0, "Pearson"
        SPEARMAN = 1, "Spearman"
        # R-squared:
        SIMPLE = 2, "Simple Linear"
        PARTIAL = 3, "Partial"
        MULTIPLE = 4, "Multiple"
        QUANTILE = 5, "Quantile"
        # Ratio:
        RESPONSE = 6, "Response ratio"
        ODDS = 7, "Odds ratio"
        RISK = 8, "Risk ratio"
        HAZARD = 9, "Hazard ratio"
        # Meandiff:
        NONSTAND = 10, "Non-standardized"
        STAND = 11, "Standardized"
        # Slope:
        NONTRANSFORMED = 12, "Non-transformed data"
        TRANSFORMED = 13, "Transformed data"
        # Ordination choices
        CCA = 14, "Canonical correspondence analysis (CCA)"
        PCA = 15, "Principal components analysis (PCA)"
        MDA = 16, "Multiple discriminant analysis (MDA)"
        NMDS = 17, "Non-multidimensional scaling (NMDS)"
        FACTOR = 18, "Factor analysis"
        # Threshold choices
        REGTREE = 19, "Regression tree"
        RANDOMFOREST = 20, "Random forest"
        BREAKPOINT = 21, "Breakpoint (piecewise) regression"
        QUANTREG = 22, "Quantile regression"
        CFD = 23, "Cumulative frequency distribution"
        GFA = 24, "Gradient forest analysis"
        NONLINEAR = 25, "Non-linear curve fitting"
        ORDINATION = 26, "Ordination"
        TITAN = 27, "TITAN"
        # option for each category
        NS = 28, "Not specified"


class Variability(models.IntegerChoices):
    CI95 = 0, "95% CI"
    CI90 = 1, "90% CI"
    SD = 2, "Standard deviation"
    SE = 3, "Standard error"
    NA = 4, "Not applicable"


class StatisticalSigType(models.IntegerChoices):
    PVAL = 0, "P-value"
    FSTAT = 1, "F statistic"
    CHISQ = 2, "Chi square"
    NA = 3, "Not applicable"
