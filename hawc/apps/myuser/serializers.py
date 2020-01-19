from rest_framework import serializers

from ..utils.helper import SerializerHelper
from . import models


class HAWCUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        model = models.HAWCUser
        fields = (
            "id",
            "full_name",
        )


SerializerHelper.add_serializer(models.HAWCUser, HAWCUserSerializer)
