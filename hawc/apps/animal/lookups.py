from typing import Any
from django.forms import ValidationError
from django.utils.safestring import mark_safe
from selectable.registry import registry

from ..common.lookups import DistinctStringLookup, RelatedDistinctStringLookup, RelatedLookup
from . import models


class RelatedExperimentCASLookup(RelatedDistinctStringLookup):
    model = models.Experiment
    distinct_field = "cas"
    related_filter = "study__assessment_id"


class ExperimentByStudyLookup(RelatedLookup):
    model = models.Experiment
    search_fields = ("name__icontains",)
    related_filter = "study_id"


class AnimalGroupByExperimentLookup(RelatedLookup):
    model = models.AnimalGroup
    search_fields = ("name__icontains",)
    related_filter = "experiment_id"


class RelatedAnimalGroupLifestageExposedLookup(RelatedDistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_exposed"
    related_filter = "experiment__study__assessment_id"


class RelatedAnimalGroupLifestageAssessedLookup(RelatedDistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_assessed"
    related_filter = "experiment__study__assessment_id"


class RelatedEndpointSystemLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "system"
    related_filter = "assessment_id"


class RelatedEndpointOrganLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "organ"
    related_filter = "assessment_id"


class RelatedEndpointEffectLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect"
    related_filter = "assessment_id"


class RelatedEndpointEffectSubtypeLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect_subtype"
    related_filter = "assessment_id"


class ExpChemicalLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "chemical"


class ExpCasLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "cas"


class ExpChemSourceLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "chemical_source"


class ExpGlpLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "guideline_compliance"


class EndpointSystemLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "system"


class EndpointOrganLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "organ"


class EndpointEffectLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect"


class EndpointEffectSubtypeLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect_subtype"


class EndpointStatisticalTestLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "statistical_test"


class EndpointNameLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "name"


class EndpointByStudyLookup(RelatedLookup):
    # Return names of endpoints available for a particular study
    model = models.Endpoint
    user_specified_search_fields = [
        "animal_group__experiment__name",
        "animal_group__name",
        "name",
    ]
    search_fields = (
        "name__icontains",
        "animal_group__name__icontains",
        "animal_group__experiment__name__icontains",
    )
    related_filter = "animal_group__experiment__study"
    search_fields_choices = {
        "animal_group__experiment__name",
        "animal_group__name",
        "name",
        "created",
        "last_updated",
        "data_type",
        "response_units",
        "observation_time",
        "system",
    }

    def get_item_label(self, obj):
        return " | ".join(
            [str(self.get_underscore_field_val(obj, f)) for f in self.user_specified_search_fields]
        )

    def get_item_value(self, obj):
        return self.get_item_label(obj)

    def get_query(self, request, term):
        order_by = request.GET["order_by"]
        search_fields = request.GET.get("search_fields")

        # TODO - investigate if this alters class-state; may have side effects across requests
        # preserve this so we can return a dynamic representation of the Endpoint...
        self.user_specified_search_fields = search_fields.split(",")
        for f in self.user_specified_search_fields:
            if f not in self.search_fields_choices:
                raise ValidationError(f"{f} is not a valid search field choice.")

        # TODO - investigate if this alters class-state; may have side effects across requests
        # update the search_fields tuple to match the fields we're going to show...
        self.search_fields = [f"{field}__icontains" for field in self.user_specified_search_fields]

        if len(self.search_fields) > 0:
            return super().get_query(request, term).distinct().order_by(order_by)
        else:
            return None

    def get_underscore_field_val(self, obj: Any, underscore_path: str):
        """
        Recursively select attributes from objects, given a django queryset underscore path.
        For example, `related_item__some_field__foo` will return `obj.related_item.some_field.foo`

        Args:
            obj (Any): An object
            underscore_path (str): the path to retrieve

        Returns:
            Any: the desired attribute of the object or child object.
        """

        obj_ = obj
        try:
            for attr in underscore_path.split("__"):
                obj_ = getattr(obj_, attr)
        except AttributeError:
            raise AttributeError(f"Element {underscore_path} not found in {obj}")

        return obj_


class EndpointByAssessmentLookup(RelatedLookup):
    # Return names of endpoints available for a assessment study
    model = models.Endpoint
    search_fields = (
        "name__icontains",
        "animal_group__name__icontains",
        "animal_group__experiment__name__icontains",
        "animal_group__experiment__study__short_citation__icontains",
    )
    related_filter = "assessment_id"

    def get_item_label(self, obj):
        return mark_safe(
            f"{obj.animal_group.experiment.study} | {obj.animal_group.experiment} | {obj.animal_group} | {obj}"
        )

    def get_item_value(self, obj):
        return self.get_item_label(obj)


class EndpointByAssessmentTextLookup(RelatedLookup):
    model = models.Endpoint
    search_fields = ("name__icontains",)
    related_filter = "assessment_id"

    def get_query(self, request, term):
        return super().get_query(request, term).distinct("name").order_by("name")


class EndpointIdByAssessmentLookup(EndpointByAssessmentLookup):
    def get_item_value(self, obj):
        return obj.id


class EndpointByAssessmentLookupHtml(EndpointByAssessmentLookup):
    def get_item_value(self, obj):
        return f'<a href="{obj.get_absolute_url()}" target="_blank">{self.get_item_label(obj)}</a>'


registry.register(ExperimentByStudyLookup)
registry.register(AnimalGroupByExperimentLookup)
registry.register(RelatedExperimentCASLookup)
registry.register(RelatedAnimalGroupLifestageExposedLookup)
registry.register(RelatedAnimalGroupLifestageAssessedLookup)
registry.register(RelatedEndpointSystemLookup)
registry.register(RelatedEndpointOrganLookup)
registry.register(RelatedEndpointEffectLookup)
registry.register(RelatedEndpointEffectSubtypeLookup)

registry.register(ExpChemicalLookup)
registry.register(ExpCasLookup)
registry.register(ExpChemSourceLookup)
registry.register(ExpGlpLookup)
registry.register(EndpointSystemLookup)
registry.register(EndpointOrganLookup)
registry.register(EndpointEffectLookup)
registry.register(EndpointEffectSubtypeLookup)
registry.register(EndpointStatisticalTestLookup)

registry.register(EndpointNameLookup)
registry.register(EndpointByStudyLookup)
registry.register(EndpointByAssessmentLookup)
registry.register(EndpointByAssessmentTextLookup)
registry.register(EndpointIdByAssessmentLookup)
registry.register(EndpointByAssessmentLookupHtml)
