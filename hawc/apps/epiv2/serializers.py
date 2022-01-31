from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ..common.serializers import FlexibleChoiceField, IdLookupMixin
from ..study.serializers import StudySerializer
from ..epi.serializers import StudyPopulationCountrySerializer
from . import constants, models


class AgeProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    class Meta:
        model = models.AgeProfile
        fields = ["name"]
    
    def to_internal_value(self, data):
        if type(data) is str:
            try:
                age_profile = self.Meta.model.objects.get(name__iexact=data)
                return age_profile
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"'{data}' is not a valid Age profile.")

        return super().to_internal_value(data)


class DesignSerializer(IdLookupMixin, serializers.ModelSerializer):
    study = StudySerializer()
    study_design = FlexibleChoiceField(choices=constants.StudyDesign.choices)
    source = FlexibleChoiceField(choices=constants.Source.choices)
    sex = FlexibleChoiceField(choices=constants.Sex.choices)
    countries = StudyPopulationCountrySerializer(many=True)
    age_profile = AgeProfileSerializer(many=True, read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Design
        fields = "__all__"
