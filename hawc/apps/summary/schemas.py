from pydantic import BaseModel

from . import constants


class VisualDataRequest(BaseModel):
    visual_type: constants.VisualType
