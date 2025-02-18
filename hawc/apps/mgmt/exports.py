from ..common.exports import Exporter, ModelExport
from ..study.exports import StudyExport


class TaskExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "owner_id": "owner",
            "owner_email": "owner__email",
            "type": "type",
            "type_display": "type__name",
            "status": "status",
            "status_display": "status__name",
            "due_date": "due_date",
            "started": "started",
            "completed": "completed",
        }


class TaskExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "study"),
            TaskExport("task", ""),
        ]
