from rest_framework import exceptions, serializers

from .models import Design


class BelongsToSameDesignMixin:
    """
    ex: when updating an ExposureLevel, there's a related Chemical and Exposure sometimes passed into the payload as
    "chemical_id" and "exposure_level_id". Basic DRF functionality verifies that the supplied values are valid
    items in the database, but it's a common requirement that they also belong to the same parent object; in this
    case, the same design. This mixin performs that type of validation logic.

    Could potentially generalize this even further (so that it's not just useful for "Design"); this type of
    relationship is not uncommon.
    """

    def validate(self, data):
        fields_to_check = []
        try:
            fields_to_check = self.belongs_to_same_design_fields

            # first off - were any of the parameters we're concerned with in the payload? If not, there's
            # no need to perform any custom validation.
            perform_custom_validation = False
            for field_to_check in fields_to_check:
                param_name = field_to_check[0]
                if param_name in self.initial_data:
                    perform_custom_validation = True
                    break

            if perform_custom_validation is True:
                # figure out what design we're concerned with...
                if "design" in self.initial_data:
                    # load from the supplied payload...
                    design_id = self.initial_data.get("design")
                    design = Design.objects.get(id=design_id)
                else:
                    # load from the previously saved state; the APIException here should never happen but just in case...
                    if self.instance is not None:
                        design = self.instance.design
                    else:
                        raise exceptions.APIException(
                            "validation failed; could not determine relevant design id"
                        )

            invalid_fields = []
            for field_to_check in fields_to_check:
                param_name = field_to_check[0]
                model_klass = field_to_check[1]

                if param_name in self.initial_data:
                    candidate_id = self.initial_data.get(param_name)
                    candidate_obj = model_klass.objects.get(id=candidate_id)

                    if candidate_obj.design.id != design.id:
                        invalid_fields.append(
                            (
                                param_name,
                                f"object with id={candidate_id} does not belong to the correct design.",
                            )
                        )
            if len(invalid_fields) > 0:
                raise serializers.ValidationError({x[0]: x[1] for x in invalid_fields})
        except AttributeError:
            raise Exception(
                f"{type(self).__name__} is configured to mixin BelongsToSameDesignMixin but lacks a properly configured property 'belongs_to_same_design_fields'"
            )

        return super().validate(data)
