from enum import Enum

from ...assessment.constants import EpiVersion
from ...assessment.models import Assessment
from ..constants import StudyType, VisualType
from .animal import BioassayEndpointPrefilter, BioassayStudyPrefilter
from .eco import EcoResultPrefilter
from .epi import EpiV1ResultPrefilter, EpiV1StudyPrefilter
from .epimeta import EpiMetaResultPrefilter
from .epiv2 import EpiV2ResultPrefilter, EpiV2StudyPrefilter
from .invitro import InvitroOutcomePrefilter, InvitroStudyPrefilter

__all__ = [
    "get_prefilter_cls",
]


class EndpointPrefilter(Enum):
    BIOASSAY = BioassayEndpointPrefilter
    EPIV1 = EpiV1ResultPrefilter
    EPIV2 = EpiV2ResultPrefilter
    EPI_META = EpiMetaResultPrefilter
    IN_VITRO = InvitroOutcomePrefilter
    ECO = EcoResultPrefilter


class StudyPrefilter(Enum):
    BIOASSAY = BioassayStudyPrefilter
    EPIV1 = EpiV1StudyPrefilter
    EPIV2 = EpiV2StudyPrefilter
    IN_VITRO = InvitroStudyPrefilter


def get_prefilter_cls(
    visual_type: VisualType | None, study_type: StudyType, assessment: Assessment
):
    study_type = StudyType(study_type)
    name = study_type.name
    if study_type == StudyType.EPI:
        if assessment.epi_version == EpiVersion.V1:
            name = "EPIV1"
        elif assessment.epi_version == EpiVersion.V2:
            name = "EPIV2"
    mapping = {
        None: EndpointPrefilter,
        VisualType.BIOASSAY_CROSSVIEW: EndpointPrefilter,
        VisualType.ROB_HEATMAP: StudyPrefilter,
        VisualType.ROB_BARCHART: StudyPrefilter,
    }
    return mapping[visual_type][name].value
