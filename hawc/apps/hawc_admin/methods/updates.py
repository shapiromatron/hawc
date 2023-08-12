from datetime import UTC, date, datetime, time

import pandas as pd
from django.db.models import Q

from hawc.apps.animal.models import Endpoint, Experiment
from hawc.apps.assessment.models import Assessment, AssessmentValue, Dataset
from hawc.apps.eco.models import Cause, Effect
from hawc.apps.eco.models import Design as EcoDesign
from hawc.apps.epi.models import Outcome, StudyPopulation
from hawc.apps.epiv2.models import Design, Exposure
from hawc.apps.epiv2.models import Outcome as OutcomeV2
from hawc.apps.lit.models import Reference, Search, UserReferenceTag
from hawc.apps.riskofbias.models import RiskOfBias
from hawc.apps.study.models import Study
from hawc.apps.summary.models import DataPivot, SummaryTable, Visual

from ...common.serializers import PydanticDrfSerializer


class UpdateSchema(PydanticDrfSerializer):
    before: date | None = None
    after: date | None = None
    assessment: bool = False


def _updates_content(filters: Q) -> pd.DataFrame:
    columns = "App|Model|Count".split("|")
    data = []
    for Model in [
        Assessment,
        AssessmentValue,
        Dataset,
        Reference,
        Search,
        UserReferenceTag,
        Study,
        RiskOfBias,
        Experiment,
        Endpoint,
        EcoDesign,
        Cause,
        Effect,
        StudyPopulation,
        Outcome,
        Design,
        Exposure,
        OutcomeV2,
        DataPivot,
        Visual,
        SummaryTable,
    ]:
        data.append(
            [
                Model._meta.app_label,
                Model._meta.model_name,
                Model.objects.filter(filters).count(),
            ]
        )
    return pd.DataFrame(data=data, columns=columns)


def _get_assessment_set(Model, prefix: str, filters: Q) -> tuple[set[int], set[int], set[int]]:
    return (
        set(
            Model.objects.filter(
                filters,
                **{f"{prefix}public_on__isnull": False, f"{prefix}hide_from_public_page": False},
            )
            .order_by(f"{prefix}id")
            .distinct(f"{prefix}id")
            .values_list(f"{prefix}id", flat=True)
        ),
        set(
            Model.objects.filter(
                filters,
                **{f"{prefix}public_on__isnull": False, f"{prefix}hide_from_public_page": True},
            )
            .order_by(f"{prefix}id")
            .distinct(f"{prefix}id")
            .values_list(f"{prefix}id", flat=True)
        ),
        set(
            Model.objects.filter(filters, **{f"{prefix}public_on__isnull": True})
            .order_by(f"{prefix}id")
            .distinct(f"{prefix}id")
            .values_list(f"{prefix}id", flat=True)
        ),
    )


def _updates_assessment(filters: Q) -> pd.DataFrame:
    """
    Count of assessments which had changes made within the specified date range in the
    assessment or select child models of the assessment. In many cases, because we're comparing
    the dates of dozens of models, an assessment may appear to be updated within multiple
    date ranges.
    """
    public_ids = set()
    unlisted_ids = set()
    private_ids = set()
    for model, prefix in [
        (Assessment, ""),
        (Study, "assessment__"),
        (RiskOfBias, "study__assessment__"),
        (Endpoint, "assessment__"),
        (Outcome, "assessment__"),
        (OutcomeV2, "design__study__assessment__"),
        (Visual, "assessment__"),
        (DataPivot, "assessment__"),
    ]:
        public, unlisted, private = _get_assessment_set(model, prefix, filters)
        public_ids.update(public)
        unlisted_ids.update(unlisted)
        private_ids.update(private)

    return pd.DataFrame(
        data=[
            ["Public", len(public_ids)],
            ["Unlisted", len(unlisted_ids)],
            ["Private", len(private_ids)],
        ],
        columns="Status|Count".split("|"),
    )


def updates(request) -> pd.DataFrame:
    model = UpdateSchema.from_drf(request.query_params)
    filters = Q()
    if model.after:
        filters &= Q(last_updated__gte=datetime.combine(model.after, time.min, tzinfo=UTC))
    if model.before:
        filters &= Q(last_updated__lte=datetime.combine(model.before, time.min, tzinfo=UTC))
    if model.assessment:
        return _updates_assessment(filters)
    return _updates_content(filters)
