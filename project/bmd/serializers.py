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
        ret['allModelOptions'] = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        ret['allBmrOptions'] = [{'name': 'd'}, {'name': 'e'}, {'name': 'f'}]
        return ret
