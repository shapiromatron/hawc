import json
from datetime import datetime, timedelta
from typing import Any, NamedTuple, Union

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from reversion.models import Version

from ..common.helper import HAWCDjangoJSONEncoder, map_enum
from ..common.models import BaseManager
from . import constants


class AssessmentManager(BaseManager):
    assessment_relation = "id"

    def get_public_assessments(self):
        return self.filter(public_on__isnull=False, hide_from_public_page=False).order_by("name")

    def get_viewable_assessments(self, user, exclusion_id=None, public=False):
        """
        Return queryset of all assessments which that user is able to view,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        filters = (
            Q(project_manager=user) | Q(team_members=user) | Q(reviewers=user)
            if user.is_authenticated
            else Q(pk__in=[])
        )
        if public:
            filters |= Q(public_on__isnull=False) & Q(hide_from_public_page=False)
        return self.filter(filters).exclude(id=exclusion_id).distinct()

    def get_editable_assessments(self, user, exclusion_id=None):
        """
        Return queryset of all assessments which that user is able to edit,
        optionally excluding assessment exclusion_id,
        not including public assessments
        """
        return (
            self.filter(Q(project_manager=user) | Q(team_members=user))
            .exclude(id=exclusion_id)
            .distinct()
        )

    def recent_public(self, n: int = 5) -> QuerySet:
        """Get recent public, published assessments

        Args:
            n (int, optional): Number of assessments; defaults to 5.

        Returns:
            models.QuerySet: An assessment queryset
        """
        return self.filter(public_on__isnull=False, hide_from_public_page=False).order_by(
            "-public_on"
        )[:n]


class AttachmentManager(BaseManager):
    def get_attachments(self, obj, public_only: bool):
        filters = {
            "content_type": ContentType.objects.get_for_model(obj),
            "object_id": obj.id,
        }
        if public_only:
            filters["publicly_available"] = True
        return self.filter(**filters)

    def assessment_qs(self, assessment_id):
        a = ContentType.objects.get(app_label="assessment", model="assessment").id
        return self.filter(content_type=a, object_id=assessment_id)


class DoseUnitManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.all()

    def json_all(self):
        return json.dumps(list(self.all().values()), cls=HAWCDjangoJSONEncoder)

    def get_animal_units(self, assessment):
        """
        Returns a queryset of all bioassay DoseUnits used in an assessment.
        """
        return (
            self.filter(
                dosegroup__dose_regime__dosed_animals__experiment__study__assessment=assessment
            )
            .order_by("pk")
            .distinct("pk")
        )

    def get_animal_units_names(self, assessment):
        """
        Returns a list of the dose-units which are used in the selected
        assessment for animal bioassay data.
        """
        return self.get_animal_units(assessment).values_list("name", flat=True)

    def get_iv_units(self, assessment_id: int):
        return (
            self.filter(ivexperiments__study__assessment=assessment_id)
            .order_by("id")
            .distinct("id")
        )

    def get_epi_units(self, assessment_id: int):
        return (
            self.filter(exposure__study_population__study__assessment_id=assessment_id)
            .order_by("pk")
            .distinct("pk")
        )


class SpeciesManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.all()


class StrainManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.all()


class EffectTagManager(BaseManager):
    assessment_relation = "baseendpoint__assessment"

    def assessment_qs(self, assessment_id):
        return self.filter(baseendpoint__assessment_id=assessment_id).distinct()

    def get_choices(self, assessment_id):
        return self.get_qs(assessment_id).values_list("id", "name").order_by("name")


class BaseEndpointManager(BaseManager):
    assessment_relation = "assessment"


class TimeSpentEditingManager(BaseManager):
    assessment_relation = "assessment"


class DatasetManager(BaseManager):
    assessment_relation = "assessment"


class AssessmentValueManager(BaseManager):
    assessment_relation = "assessment"

    def get_df(self) -> pd.DataFrame:
        """Get a dataframe of Assessment Values from given Queryset of Values."""
        mapping: dict[str, str] = {
            "assessment_id": "assessment_id",
            "assessment__name": "assessment_name",
            "assessment__created": "assessment_created",
            "assessment__last_updated": "assessment_last_updated",
            "assessment__details__project_type": "project_type",
            "assessment__details__project_status": "project_status",
            "assessment__details__project_url": "project_url",
            "assessment__details__peer_review_status": "peer_review_status",
            "assessment__details__qa_id": "qa_id",
            "assessment__details__qa_url": "qa_url",
            "assessment__details__report_id": "report_id",
            "assessment__details__report_url": "report_url",
            "assessment__details__extra": "assessment_extra",
            "evaluation_type": "evaluation_type",
            "id": "value_id",
            "system": "system",
            "value_type": "value_type",
            "value": "value",
            "value_unit__name": "value_unit",
            "basis": "basis",
            "pod_value": "pod_value",
            "pod_unit__name": "pod_unit",
            "species_studied": "species_studied",
            "duration": "duration",
            "study_id": "study_id",
            "study__short_citation": "study_citation",
            "confidence": "confidence",
            "uncertainty": "uncertainty",
            "tumor_type": "tumor_type",
            "extrapolation_method": "extrapolation_method",
            "evidence": "evidence",
            "comments": "comments",
            "extra": "extra",
        }
        data = self.select_related("assessment__details").values_list(*list(mapping.keys()))
        df = pd.DataFrame(data=data, columns=list(mapping.values())).sort_values(
            ["assessment_id", "value_id"]
        )
        map_enum(df, "project_status", constants.Status, replace=True)
        map_enum(df, "peer_review_status", constants.PeerReviewType, replace=True)
        map_enum(df, "evaluation_type", constants.EvaluationType, replace=True)
        map_enum(df, "value_type", constants.ValueType, replace=True)
        map_enum(df, "confidence", constants.Confidence, replace=True)
        return df


class AssessmentDetailManager(BaseManager):
    assessment_relation = "assessment"


class Event(NamedTuple):
    """A potentially collapsed changed event between Logs and Reversions"""

    message: str
    snapshot: str
    user: Any
    created: datetime


class EventPair:
    """An Event Pair Comparison between a Log and Reversion"""

    def __init__(self, item_1, item_2=None):
        """Build an event pair, or at least one event.

        Args:
            item_1 (Union[Log, Version]): The first item in the pair
            item_2 (Union[Log, Version], optional): The optional second item in the pair
        """
        self.log = None
        self.version = None
        if isinstance(item_1, Version):
            self.version = item_1
        else:
            self.log = item_1
        if item_2:
            if isinstance(item_2, Version):
                self.version = item_2
            else:
                self.log = item_2

    def collapsable(self) -> bool:
        # should the two items be collapsed?
        if self.log is None or self.version is None:
            return False
        return abs(self.log.created - self.version.revision.date_created) < timedelta(seconds=10)

    def output(self) -> Event:
        # Return a collapsed event
        return Event(
            message=self.log.message if self.log else "",
            snapshot=self.version.serialized_data if self.version else "",
            user=self.log.user if self.log else self.version.revision.user,
            created=self.log.created if self.log else self.version.revision.date_created,
        )


class LogManager(BaseManager):
    assessment_relation = "assessment"

    def get_object_audit(
        self, content_type: Union[ContentType, int], object_id: int
    ) -> list[Event]:
        """
        Combines information from HAWC's internal logs and reversion logs for a more complete audit.
        Matching is attempted between these two log types to account for same operations.

        Args:
            content_type (Union[ContentType, int]): Content type of interested object.
            object_id (int): ID of interested object.

        Returns:
            list[Event]: Serialized logs with message, snapshot, user, and date created.
        """
        # sort all events in descending order
        logs = (
            self.filter(content_type=content_type, object_id=object_id)
            .select_related("user")
            .order_by("id")
        )
        versions = (
            Version.objects.filter(content_type=content_type, object_id=object_id)
            .select_related("revision__user")
            .order_by("id")
        )
        events = list(logs) + list(versions)
        events.sort(
            key=lambda el: el.created if isinstance(el, self.model) else el.revision.date_created,
            reverse=True,
        )

        # build event aggregations
        aggregations = []
        used_next_event = None
        for i, this_event in enumerate(events):
            # skip current item if we've already used it
            if this_event is used_next_event:
                continue

            # try to get next event to compare; if we dont have one, add the current
            try:
                next_event = events[i + 1]
            except IndexError:
                aggregations.append(EventPair(this_event).output())
                break

            # run pair comparisons
            pair = EventPair(this_event, next_event)
            if pair.collapsable():
                # add both; mark second as consumed
                aggregations.append(pair.output())
                used_next_event = next_event
            else:
                # just add one
                aggregations.append(EventPair(this_event).output())

        return aggregations
