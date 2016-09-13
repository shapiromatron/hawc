from rest_framework import serializers

from myuser.serializers import HAWCUserSerializer
from study.serializers import StudyAssessmentSerializer, SimpleStudySerializer

from . import models


class TaskSerializer(serializers.ModelSerializer):
    owner = HAWCUserSerializer(read_only=True)
    study = SimpleStudySerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = models.Task
        fields = '__all__'
        read_only_fields = (
            'id',
            'study',
            'open',
        )


class TaskByAssessmentSerializer(TaskSerializer):
    study = StudyAssessmentSerializer(read_only=True)

    class Meta(TaskSerializer.Meta):
        depth = 2
