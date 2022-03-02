from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from hawc.apps.assessment.models import Assessment

from ...models import LiteratureAssessment
from ...tasks import rerun_topic_model


class Command(BaseCommand):
    help = """Run literature topic model for selected assessment(s)"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--assessment",
            type=int,
            help="Assessment ID to modify; defaults to all assessments",
            default=-1,
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["assessment"] > 0:
            assessments = Assessment.objects.filter(id=options["assessment"])
        else:
            assessments = Assessment.objects.all().order_by("id")

        LiteratureAssessment.objects.filter(assessment__in=assessments).update(
            topic_tsne_refresh_requested=now()
        )
        for assessment in assessments:
            rerun_topic_model(assessment.id)
