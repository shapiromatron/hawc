from rest_framework import serializers

from . import models


class StudySerializer(serializers.ModelSerializer):

    url = serializers.CharField(source='get_absolute_url', read_only=True)

    def transform_study_type(self, obj, value):
        return obj.get_study_type_display()

    def transform_coi_reported(self, obj, value):
        return obj.get_coi_reported_display();

    class Meta:
        model = models.Study
        depth = 0
