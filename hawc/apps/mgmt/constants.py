from django.db import models


class TaskType(models.IntegerChoices):
    PREPARATION = 10, "Preparation"
    EXTRACTION = 20, "Data Extraction"
    QA = 30, "QA/QC"
    ROB = 40, "Study Evaluation"


class TaskStatus(models.IntegerChoices):
    NOT_STARTED = 10, "Not Started"
    STARTED = 20, "Started"
    COMPLETED = 30, "Completed"
    ABANDONED = 40, "Abandoned"

    @classmethod
    def extra_choices(cls):
        return [(990, "Active"), (995, "Inactive")]

    @classmethod
    def filter_extra(cls, value: int) -> models.Q:
        if value == 990:
            return models.Q(status__terminal_status=False)
        elif value == 995:
            return models.Q(status__terminal_status=True)
        else:
            return models.Q(status=value)

    @classmethod
    def status_colors(cls, value: int):
        colors = {
            10: "#CFCFCF",
            20: "#FFCC00",
            30: "#00CC00",
            40: "#CC3333",
        }
        return colors.get(value)


class StartTaskTriggerEvent(models.IntegerChoices):
    STUDY_CREATION = 10, "Create Study"
    DATA_EXTRACTION = 20, "Data Extraction"
    MODIFY_ROB = 30, "Modify Study Evaluation"
    COMPLETE_ROB = 40, "Complete Study Evaluation"
