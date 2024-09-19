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
            "due_date": "due_date",
            "started": "started",
            "completed": "completed",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "type_display": sql_display(query_prefix + "type", constants.TaskType),
            "status_display": sql_display(query_prefix + "status", constants.TaskStatus),
        }


class TaskExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "study"),
            TaskExport("task", ""),
        ]
