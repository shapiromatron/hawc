from enum import Enum

import pandas as pd

from ..models import Assessment
from ...common.helper import FlatExport
from ...common.serializers import PydanticDrfSerializer


class AuditType(str, Enum):
    ASSESSMENT = "assessment"


class AssessmentAuditSerializer(PydanticDrfSerializer):
    assessment: Assessment
    type: AuditType

    class Config:
        arbitrary_types_allowed = True

    def export(self) -> FlatExport:
        df = pd.DataFrame(data=[[1, 2, 3], [4, 5, 6]], columns="a b c".split())
        export = FlatExport(df=df, filename="merp")
        return export
