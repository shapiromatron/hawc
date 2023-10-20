from enum import Enum
from typing import Self

from ...assessment.constants import EpiVersion
from ...assessment.models import Assessment
from ..constants import StudyType, VisualType
from .animal import BioassayEndpointPrefilter, BioassayStudyPrefilter
from .eco import EcoResultPrefilter
from .epi import EpiV1ResultPrefilter
from .epimeta import EpiMetaResultPrefilter
from .epiv2 import EpiV2ResultPrefilter
from .invitro import InvitroOutcomePrefilter

__all__ = [
    "BioassayEndpointPrefilter",
    "BioassayStudyPrefilter",
    "EpiV1ResultPrefilter",
    "EpiV2ResultPrefilter",
    "EpiMetaResultPrefilter",
    "InvitroOutcomePrefilter",
    "EcoResultPrefilter",
    "StudyTypePrefilter",
    "VisualTypePrefilter",
]


class StudyTypePrefilter(Enum):
    BIOASSAY = BioassayEndpointPrefilter
    EPIV1 = EpiV1ResultPrefilter
    EPIV2 = EpiV2ResultPrefilter
    EPI_META = EpiMetaResultPrefilter
    IN_VITRO = InvitroOutcomePrefilter
    ECO = EcoResultPrefilter

    @classmethod
    def from_study_type(cls, study_type: int | StudyType, assessment: Assessment) -> Self:
        study_type = StudyType(study_type)
        name = study_type.name
        if study_type == StudyType.EPI:
            if assessment.epi_version == EpiVersion.V1:
                name = "EPIV1"
            elif assessment.epi_version == EpiVersion.V2:
                name = "EPIV2"
        return cls[name]


class VisualTypePrefilter(Enum):
    BIOASSAY_CROSSVIEW = BioassayEndpointPrefilter
    ROB_HEATMAP = BioassayStudyPrefilter
    ROB_BARCHART = BioassayStudyPrefilter

    @classmethod
    def from_visual_type(cls, visual_type: int | VisualType) -> Self:
        visual_type = VisualType(visual_type)
        name = visual_type.name
        return cls[name]
