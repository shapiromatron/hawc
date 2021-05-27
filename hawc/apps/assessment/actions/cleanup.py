from typing import Dict

from django.apps import apps
from django.db.models import Count
from django.urls import reverse

from ..models import Assessment


def endpoint_cleanup_metadata(assessment: Assessment) -> Dict:

    # re-query w/ annotations
    assessment = (
        Assessment.objects.get_qs(assessment.id)
        .annotate(endpoint_count=Count("baseendpoint__endpoint"))
        .annotate(outcome_count=Count("baseendpoint__outcome"))
        .annotate(ivendpoint_count=Count("baseendpoint__ivendpoint"))
    ).first()
    app_url = reverse("assessment:clean_extracted_data", args=(assessment.id,))

    items = [
        # lit
        {
            "count": apps.get_model("lit", "Reference").objects.get_qs(assessment.id).count(),
            "title": "references",
            "type": "reference",
            "url": f"{app_url}reference/",
            "url_cleanup_list": reverse("lit:api:reference-cleanup-list"),
            "modal_key": "Study",
        },
        # study
        {
            "count": apps.get_model("study", "Study").objects.get_qs(assessment.id).count(),
            "title": "studies",
            "type": "study",
            "url": f"{app_url}study/",
            "url_cleanup_list": reverse("study:api:study-cleanup-list"),
            "modal_key": "Study",
        },
        # animal
        {
            "count": assessment.endpoint_count,
            "title": "animal bioassay endpoints",
            "type": "ani",
            "url": f"{app_url}ani/",
            "url_cleanup_list": reverse("animal:api:endpoint-cleanup-list"),
            "modal_key": "Endpoint",
        },
        {
            "count": apps.get_model("animal", "Experiment").objects.get_qs(assessment.id).count(),
            "title": "animal bioassay experiments",
            "type": "experiment",
            "url": f"{app_url}experiment/",
            "url_cleanup_list": reverse("animal:api:experiment-cleanup-list"),
            "modal_key": "Experiment",
        },
        {
            "count": apps.get_model("animal", "AnimalGroup").objects.get_qs(assessment.id).count(),
            "title": "animal bioassay animal groups",
            "type": "animal-groups",
            "url": f"{app_url}animal-groups/",
            "url_cleanup_list": reverse("animal:api:animal_group-cleanup-list"),
            "modal_key": "AnimalGroup",
        },
        {
            "count": apps.get_model("animal", "DosingRegime").objects.get_qs(assessment.id).count(),
            "title": "animal bioassay dosing regimes",
            "type": "dosing-regime",
            "url": f"{app_url}dosing-regime/",
            "url_cleanup_list": reverse("animal:api:dosingregime-cleanup-list"),
            "modal_key": "AnimalGroup",
        },
        # epi
        {
            "count": assessment.outcome_count,
            "title": "epidemiological outcomes assessed",
            "type": "epi",
            "url": f"{app_url}epi/",
            "url_cleanup_list": reverse("epi:api:outcome-cleanup-list"),
            "modal_key": "Outcome",
        },
        {
            "count": apps.get_model("epi", "StudyPopulation").objects.get_qs(assessment.id).count(),
            "title": "epi study populations",
            "type": "study-populations",
            "url": f"{app_url}study-populations/",
            "url_cleanup_list": reverse("epi:api:studypopulation-cleanup-list"),
            "modal_key": "StudyPopulation",
        },
        {
            "count": apps.get_model("epi", "Exposure").objects.get_qs(assessment.id).count(),
            "title": "epi exposures",
            "type": "exposures",
            "url": f"{app_url}exposures/",
            "url_cleanup_list": reverse("epi:api:exposure-cleanup-list"),
            "modal_key": "Exposure",
        },
        # in vitro
        {
            "count": assessment.ivendpoint_count,
            "title": "in vitro endpoints",
            "type": "in-vitro",
            "url": f"{app_url}in-vitro/",
            "url_cleanup_list": reverse("invitro:api:ivendpoint-cleanup-list"),
            "modal_key": "IVEndpoint",
        },
        {
            "count": apps.get_model("invitro", "ivchemical").objects.get_qs(assessment.id).count(),
            "title": "in vitro chemicals",
            "type": "in-vitro-chemical",
            "url": f"{app_url}in-vitro-chemical/",
            "url_cleanup_list": reverse("invitro:api:ivchemical-cleanup-list"),
            "modal_key": "IVChemical",
        },
    ]
    return {"name": assessment.name, "id": assessment.id, "items": items}
