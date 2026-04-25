import pandas as pd
from django.utils import timezone

from ..common.exports import Exporter, ModelExport
from ..common.models import sql_display
from ..study.exports import StudyExport
from . import constants


class TaskExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "owner_id": "owner",
            "owner_email": "owner__email",
            "type": "type",
            "type_display": "type_display",
            "status": "status",
            "status_display": "status_display",
            "open": "open",
            "due_date": "due_date",
            "started": "started",
            "completed": "completed",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "type_display": sql_display(query_prefix + "type", constants.TaskType),
            "status_display": sql_display(query_prefix + "status", constants.TaskStatus),
        }

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare_df(df)
        tz = timezone.get_default_timezone()
        for key in [
            self.get_column_name("due_date"),
            self.get_column_name("started"),
            self.get_column_name("completed"),
        ]:
            if key in df.columns and not df[key].isnull().all():
                df[key] = (
                    pd.to_datetime(df[key], errors="coerce")  # contains NaT
                    .dt.tz_convert(tz)
                    .dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                )
        return df


class TaskExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "study"),
            TaskExport("task", ""),
        ]
