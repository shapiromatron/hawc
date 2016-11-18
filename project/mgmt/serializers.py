from rest_framework import serializers

from myuser.models import HAWCUser
from myuser.serializers import HAWCUserSerializer
from study.serializers import StudyAssessmentSerializer, SimpleStudySerializer

from . import models


class TaskSerializer(serializers.ModelSerializer):
    owner = HAWCUserSerializer(read_only=True)
    study = StudyAssessmentSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = models.Task
        fields = '__all__'
        read_only_fields = (
            'id',
            'study',
            'open',
            'started',
            'completed',
        )

    def update(self, instance, validated_data):
        if self.initial_data['owner']:
            owner_id = self.initial_data['owner']['id']
            instance.owner = HAWCUser.objects.get(pk=owner_id)
            instance.save()
        return super(TaskSerializer, self).update(instance, validated_data)


class TaskByAssessmentSerializer(TaskSerializer):
    study = StudyAssessmentSerializer(read_only=True)

    class Meta(TaskSerializer.Meta):
        depth = 2
