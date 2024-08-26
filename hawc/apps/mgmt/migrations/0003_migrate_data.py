# Generated by Django 5.0.6 on 2024-08-16 19:29

from django.db import migrations

# hardcoded due to possible changes/removal of constants
statuses = [(10, "Not Started"), (20, "Started"), (30, "Completed"), (40, "Abandoned")]

types = [(10, "Preparation"), (20, "Data Extraction"), (30, "QA/QC"), (40, "Study Evaluation")]


def migrate_tasks(apps, schema_editor):
    Task = apps.get_model("mgmt", "Task")
    TaskType = apps.get_model("mgmt", "TaskType")
    TaskStatus = apps.get_model("mgmt", "TaskStatus")
    Assessment = apps.get_model("assessment", "Assessment")

    # create all possible types/statuses for each assessment
    status_instances = []
    type_instances = []

    for assessment in Assessment.objects.filter(enable_project_management=True):
        for value, name in statuses:
            status_instances.append(
                TaskStatus(
                    assessment=assessment,
                    name=name,
                    value=value,
                    order=value,
                    color=get_status_color(value),
                    terminal_status=get_terminal(name),
                )
            )

        for value, name in types:
            type_instances.append(
                TaskType(
                    assessment=assessment,
                    name=name,
                    order=value,
                )
            )

    TaskStatus.objects.bulk_create(status_instances)
    TaskType.objects.bulk_create(type_instances)

    for task in Task.objects.all():
        assessment_instance = task.study.assessment

        # map new foreign keys to connected items
        task.new_type = TaskType.objects.get(
            assessment=assessment_instance, name=task.get_type_display(), order=task.type
        )
        task.new_status = TaskStatus.objects.get(
            assessment=assessment_instance,
            name=task.get_status_display(),
            value=task.status,
        )
        task.new_type.created = task.started
        task.new_type.created = task.started
        task.save()


def get_terminal(status):
    if status == "Completed" or status == "Abandoned":
        return True
    else:
        return False


def get_status_color(val):
    colors = {
        10: "#CFCFCF",
        20: "#FFCC00",
        30: "#00CC00",
        40: "#CC3333",
    }
    return colors.get(val)


class Migration(migrations.Migration):
    dependencies = [
        ("mgmt", "0002_add_new_task_models_schema"),
    ]

    operations = [
        migrations.RunPython(migrate_tasks),
    ]
