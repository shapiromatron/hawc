from rest_framework import serializers

from utils.helper import SerializerHelper

from . import models


class HAWCUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = models.HAWCUser
        fields = ('id', 'first_name', 'last_name', 'email', 'is_staff', 'full_name')

SerializerHelper.add_serializer(models.HAWCUser, HAWCUserSerializer)
