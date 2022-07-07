import json

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet

from ..common.helper import HAWCDjangoJSONEncoder
from ..common.models import BaseManager


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
