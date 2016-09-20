from utils.models import BaseManager

import logging

from study.models import Study


class TaskManager(BaseManager):
    assessment_relation = 'study__assessment'

    def owned_by(self, user):
        return self.filter(owner=user)

    def create_assessment_tasks(self, assessment):
        """
        Create tasks for all studies in assessment and save to database.

        Tasks are only added, not removed with changes. Method called via
        signal whenever assessment is created/modified.
        """
        studies = Study.objects\
            .assessment_qs(assessment.id)\
            .prefetch_related('tasks')
        tasks = []
        for study in studies:
            tasks.extend(self._get_missing_tasks(study, assessment))
        logging.info(u'Creating {} tasks for assessment {}.'.format(len(tasks), assessment.id))
        self.bulk_create(tasks)

    def _get_missing_tasks(self, study, assessment):
        """Return list of unsaved Task objects for single study."""
        existing_tasks = study.tasks.all()
        new_tasks = []

        def task_by_type(qs, task_type):
            """Get task if exists in qs, else return None."""
            for task in qs:
                if task.type == task_type:
                    return task
            return None

        # create prep task
        task = task_by_type(existing_tasks, self.model.TYPE_PREPARATION)
        if task is None:
            new_tasks.append(self.model(
                study=study,
                type=self.model.TYPE_PREPARATION
            ))

        # create extraction tasks
        if assessment.enable_data_extraction:

            task = task_by_type(existing_tasks, self.model.TYPE_EXTRACTION)
            if task is None:
                new_tasks.append(self.model(
                    study=study,
                    type=self.model.TYPE_EXTRACTION
                ))

            task = task_by_type(existing_tasks, self.model.TYPE_QA)
            if task is None:
                new_tasks.append(self.model(
                    study=study,
                    type=self.model.TYPE_QA
                ))

        # create rob tasks
        if assessment.enable_risk_of_bias:
            task = task_by_type(existing_tasks, self.model.TYPE_ROB)
            if task is None:
                new_tasks.append(self.model(
                    study=study,
                    type=self.model.TYPE_ROB
                ))

        return new_tasks

