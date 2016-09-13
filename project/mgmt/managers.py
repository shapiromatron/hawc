from django.apps import apps
from utils.models import BaseManager


class TaskManager(BaseManager):
    assessment_relation = 'study__assessment'

    def owned_by(self, user):
        return self.filter(owner=user)

    def setup_tasks_assessment(self, assessment):
        # Ensure tasks are synced w/ possible change in assessment. Tasks are
        # only added; not removed with changes. Method called whenever an
        # assessment is changed.

        def get_task(tasks, task_type):
            # get task if exists in list, else return None.
            for task in tasks:
                if task.type == task_type:
                    return task
            return None

        # only create tasks if studies exist
        Study = apps.get_model('study', 'Study')
        studies = Study.objects.assessment_qs(assessment.id).prefetch_related('tasks')
        tasks = []
        for study in studies:

            # create prep task
            task = get_task(study.tasks.all(), self.model.TYPE_PREPARATION)
            if task is None:
                tasks.append(self.model(
                    study=study,
                    type=self.model.TYPE_PREPARATION
                ))

            # create extraction tasks
            if assessment.enable_data_extraction:

                task = get_task(study.tasks.all(), self.model.TYPE_EXTRACTION)
                if task is None:
                    tasks.append(self.model(
                        study=study,
                        type=self.model.TYPE_EXTRACTION
                    ))

                task = get_task(study.tasks.all(), self.model.TYPE_QA)
                if task is None:
                    tasks.append(self.model(
                        study=study,
                        type=self.model.TYPE_QA
                    ))

            # create rob tasks
            if assessment.enable_risk_of_bias:
                task = get_task(study.tasks.all(), self.model.TYPE_ROB)
                if task is None:
                    tasks.append(self.model(
                        study=study,
                        type=self.model.TYPE_ROB
                    ))

        self.bulk_create(tasks)
