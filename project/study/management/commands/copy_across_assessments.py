from django.core.management.base import BaseCommand, CommandError

from assessment.models import Assessment
from riskofbias.models import RiskOfBias
from study.models import Study


HELP_TEXT = """Copy animal studies and risk of bias data from assessment 126 to assessment 405. """


class Command(BaseCommand):
    help = HELP_TEXT

    def handle(self, *args, **options):
        # copy animal studies to assessment 405
        source_assessment = Assessment.objects.get(pk=126)
        source_studies = Study.objects.filter(assessment=source_assessment)
        source_robs = RiskOfBias.objects.filter(study__in=source_studies)
        target_assessment = Assessment.objects.get(pk=405)
        crosswalk = Study.copy_across_assessments(source_studies, target_assessment)


        # copy risk of bias data
        # copy domains and metrics to assessment
        first_PM = target_assessment.project_manager.first()
        for domain in source_assessment.rob_domains.all():
            metrics = list(domain.metrics.all())  # force evaluation
            old_domain_id = domain.id
            domain.id = None
            domain.name = "{} (copied from {})".format(domain.name, source_assessment)
            domain.assessment = target_assessment
            domain.save()
            crosswalk['domain'][old_domain_id] = domain.id
            for metric in metrics:
                old_metric_id = metric.id
                metric.id = None
                metric.domain = domain
                metric.save()
                crosswalk['metric'][old_metric_id] = metric.id

        # copy reviews and scores
        for rob in source_robs:
            scores = list(rob.scores.all())
            rob.id = None
            rob.study_id = crosswalk[Study.COPY_NAME][rob.study_id]
            # assign author to a project manager if the author isn't a team member of the assessment.
            if not target_assessment.user_can_edit_object(rob.author):
                rob.author = first_PM
            rob.save()
            for score in scores:
                score.id = None
                score.riskofbias_id = rob.id
                score.metric_id = crosswalk['metric'][score.metric_id]
                score.save()
