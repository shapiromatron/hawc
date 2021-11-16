from rest_framework import serializers

from ..common.helper import SerializerHelper
from ..myuser.models import HAWCUser
from ..myuser.serializers import HAWCUserSerializer
from ..study.models import Study
from ..study.serializers import StudyAssessmentSerializer
from . import models


class TaskSerializer(serializers.ModelSerializer):
    owner = HAWCUserSerializer(read_only=True)
    study = StudyAssessmentSerializer(read_only=True)
    study_id = serializers.PrimaryKeyRelatedField(
        queryset=Study.objects.all(), source="study", write_only=True
    )
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = models.Task
        fields = "__all__"
        read_only_fields = (
            "id",
            "open",
            "started",
            "completed",
        )

    def update(self, instance, validated_data):
        if "owner" in self.initial_data:
            if self.initial_data["owner"] is None:
                instance.owner_id = None
            else:
                owner_id = self.initial_data["owner"]["id"]
                instance.owner = HAWCUser.objects.get(pk=owner_id)
            instance.save()
        return super().update(instance, validated_data)


class TaskByAssessmentSerializer(TaskSerializer):
    study = StudyAssessmentSerializer(read_only=True)

    class Meta(TaskSerializer.Meta):
        depth = 2


SerializerHelper.add_serializer(models.Task, TaskSerializer)
