from rest_framework import serializers

from . import models


class BMDSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BMDSession
        fields = ('id', )

    def to_representation(self, instance):
        ret = super(BMDSessionSerializer, self).to_representation(instance)
        ret['models'] = []
        ret['bmrs'] = []
        ret['allModelOptions'] = instance.get_model_options()
        ret['allBmrOptions'] = instance.get_bmr_options()
        return ret
