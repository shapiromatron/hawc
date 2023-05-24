from django.db import models
from rest_framework import serializers

from .models import Design


class SameDesignSerializerMixin:
    """
    ex: when updating an ExposureLevel, there's a related Chemical and Exposure sometimes passed into the payload as
    "chemical_id" and "exposure_level_id". Basic DRF functionality verifies that the supplied values are valid
    items in the database, but it's a common requirement that they also belong to the same parent object; in this
    case, the same design. This mixin performs that type of validation logic.

    Could potentially generalize this even further (so that it's not just useful for "Design"); this type of
    relationship is not uncommon.
    """

    same_design_fields: list[tuple[str, type[models.Model]]]

    def _get_contextual_design(self):
        # figure out what design we're concerned with...
        design = None

        if "design" in self.initial_data:
            # load from the supplied payload...
            design_id = self.initial_data.get("design")
            try:
                design = Design.objects.get(id=design_id)
            except Design.DoesNotExist:
                design = None
        elif self.instance is not None:
            # load from the previously saved state
            design = self.instance.design

        # this should never happen -- default validation should prevent it if a bad design id is
        # passed in initial_data. But just in case:
        if design is None:
            raise serializers.ValidationError({"design": "could not determine contextual design"})

        return design

    def validate(self, data):
        validated_data = super().validate(data)

        # first off - were any of the parameters we're concerned with in the payload? If not, there's
        # no need to perform any custom validation.
        perform_custom_validation = any(
            [field_name in self.initial_data for field_name, _ in self.same_design_fields]
        )

        if perform_custom_validation is False:
            return validated_data
        else:
            design = self._get_contextual_design()

            invalid_fields = {}
            for param_name, model_klass in self.same_design_fields:
                if param_name in self.initial_data:
                    candidate_id = self.initial_data.get(param_name)
                    candidate_obj = model_klass.objects.get(id=candidate_id)

                    if candidate_obj.design.id != design.id:
                        invalid_fields[
                            param_name
                        ] = f"object with id={candidate_id} does not belong to the correct design."
            if invalid_fields:
                raise serializers.ValidationError(invalid_fields)

            return validated_data
