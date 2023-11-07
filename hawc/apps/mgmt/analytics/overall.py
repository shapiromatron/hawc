import logging

from django.apps import apps
from django.db.models import Count
from django.utils import timezone

from ...common.helper import cacheable

logger = logging.getLogger(__name__)


def percentage(numerator, denominator) -> float:
    """Calculate a percentage; handles division by zero in denominator."""
    try:
        return numerator / float(denominator)
    except ZeroDivisionError:
        return 0


def _compute_object_counts() -> dict:
    """Compute object counts in HAWC. This uses a large number of queries."""
    updated = timezone.now()
    Assessment = apps.get_model("assessment", "Assessment")

    users = apps.get_model("myuser", "HAWCUser").objects.count()

    assessments = Assessment.objects.count()

    references = apps.get_model("lit", "Reference").objects.count()

    tags = apps.get_model("lit", "ReferenceTags").objects.count()

    references_tagged = (
        apps.get_model("lit", "ReferenceTags").objects.distinct("content_object_id").count()
    )

    assessments_with_studies = (
        apps.get_model("study", "Study")
        .objects.values_list("assessment_id", flat=True)
        .distinct()
        .count()
    )

    studies = apps.get_model("study", "Study").objects.count()

    rob_scores = apps.get_model("riskofbias", "RiskOfBiasScore").objects.count()

    studies_with_rob = (
        apps.get_model("study", "Study")
        .objects.annotate(robc=Count("riskofbiases"))
        .filter(robc__gt=0)
        .count()
    )

    endpoints = apps.get_model("animal", "Endpoint").objects.count()

    endpoints_with_data = (
        apps.get_model("animal", "EndpointGroup")
        .objects.order_by("endpoint_id")
        .distinct("endpoint_id")
        .count()
    )

    outcomes = apps.get_model("epi", "Outcome").objects.count()

    results = apps.get_model("epi", "Result").objects.count()

    results_with_data = (
        apps.get_model("epi", "GroupResult")
        .objects.order_by("result_id")
        .distinct("result_id")
        .count()
    )

    iv_endpoints = apps.get_model("invitro", "IVEndpoint").objects.count()

    iv_endpoints_with_data = (
        apps.get_model("invitro", "IVEndpointGroup")
        .objects.order_by("endpoint_id")
        .distinct("endpoint_id")
        .count()
    )

    visuals = (
        apps.get_model("summary", "Visual").objects.count()
        + apps.get_model("summary", "DataPivot").objects.count()
    )

    assessments_with_visuals = len(
        set(
            Assessment.objects.order_by("-created")
            .annotate(vc=Count("visuals"))
            .filter(vc__gt=0)
            .values_list("id", flat=True)
        ).union(
            set(
                Assessment.objects.order_by("-created")
                .annotate(dp=Count("datapivot"))
                .filter(dp__gt=0)
                .values_list("id", flat=True)
            )
        )
    )
    logger.info("Setting about-page cache")

    return dict(
        updated=updated,
        users=users,
        assessments=assessments,
        references=references,
        tags=tags,
        references_tagged=references_tagged,
        references_tagged_percent=percentage(references_tagged, references),
        studies=studies,
        assessments_with_studies=assessments_with_studies,
        assessments_with_studies_percent=percentage(assessments_with_studies, assessments),
        rob_scores=rob_scores,
        studies_with_rob=studies_with_rob,
        studies_with_rob_percent=percentage(studies_with_rob, studies),
        endpoints=endpoints,
        endpoints_with_data=endpoints_with_data,
        endpoints_with_data_percent=percentage(endpoints_with_data, endpoints),
        outcomes=outcomes,
        results=results,
        results_with_data=results_with_data,
        results_with_data_percent=percentage(results_with_data, results),
        iv_endpoints=iv_endpoints,
        iv_endpoints_with_data=iv_endpoints_with_data,
        iv_endpoints_with_data_percent=percentage(iv_endpoints_with_data, iv_endpoints),
        visuals=visuals,
        assessments_with_visuals=assessments_with_visuals,
        assessments_with_visuals_percent=percentage(assessments_with_visuals, assessments),
    )


def get_object_counts() -> dict:
    """
    Return high level objects counts about content in HAWC.

    This method caches the computation as it requires many database queries.
    """
    key = "analytics-overall-object-counts"
    return cacheable(lambda: _compute_object_counts(), key)
