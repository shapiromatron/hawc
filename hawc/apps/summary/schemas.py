from pydantic import BaseModel

from . import constants


class VisualConfig(BaseModel):
    assessment: int
    crud: str
    dose_units: str
    instance: dict
    visual_type: constants.VisualType
    evidence_type: constants.StudyType
    initial_data: dict
    csrf: str
    cancel_url: str
    data_url: str
    endpoint_url: str
    preview_url: str
    rob_metrics: list
    api_heatmap_datasets: str
    clear_cache_url: str
    api_url: str
