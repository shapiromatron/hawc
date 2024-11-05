from pydantic import BaseModel

from ..assessment.models import Assessment
from . import constants
from .models import Visual


class VisualDataRequest(BaseModel):
    visual_type: constants.VisualType

    def mock_visual(self, assessment: Assessment) -> Visual:
        return Visual(assessment=assessment, visual_type=self.visual_type)
