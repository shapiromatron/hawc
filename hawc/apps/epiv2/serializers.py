from rest_framework import serializers

from ..common.serializers import FlexibleChoiceField, IdLookupMixin
from ..study.serializers import StudySerializer
from . import constants, models


class DesignSerializer(IdLookupMixin, serializers.ModelSerializer):
    study = StudySerializer()
    study_design = FlexibleChoiceField(choices=constants.StudyDesign.choices)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = models.Design
        fields = "__all__"
