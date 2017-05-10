from django.db import transaction
from django.core.management.base import BaseCommand

from assessment.models import Assessment
from riskofbias.models import RiskOfBiasDomain, RiskOfBias
from study.models import Study


HELP_TEXT = """Clone studies in assessment from source to target."""


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument('source_assessment_id', type=int)
        parser.add_argument('destination_assessment_id', type=int)
        parser.add_argument('--noRiskOfBias',
                            action='store_true',
                            dest='noRiskOfBias',
                            default=False,
                            help='If flag is added, RoB is not copied')

    @transaction.atomic
    def handle(self, source_assessment_id, destination_assessment_id,
               *args, **options):
        source_assessment = Assessment.objects.get(pk=source_assessment_id)
        target_assessment = Assessment.objects.get(pk=destination_assessment_id)
        source_studies = Study.objects.filter(assessment=source_assessment)

        cw = Study.copy_across_assessment(source_studies, target_assessment)

        copyRoB = not options['noRiskOfBias']
        if copyRoB:

            cw = RiskOfBiasDomain.copy_across_assessment(
                cw, source_studies, target_assessment)

            cw = RiskOfBias.copy_across_assessment(
                cw, source_studies, target_assessment)
