from rest_framework import serializers
from rest_framework.exceptions import ParseError

from . import models


class AssessmentSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super(AssessmentSerializer, self).to_representation(instance)
        ret['url'] = instance.get_absolute_url()
        return ret

    class Meta:
        model = models.Assessment


class EffectTagsSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        raise ParseError("Not implemented!")

    def to_representation(self, obj):
        # obj is a model-manager in this case; convert to list to serialize
        return list(obj.values('slug', 'name'))


class DoseUnitsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DoseUnits


class EndpointItemSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()


class AssessmentEndpointSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
    items = serializers.ListField(child=EndpointItemSerializer())


class AssessmentRootedSerializer(serializers.ModelSerializer):

    NO_PARENT = -1

    def get_parent(self, assessment_id, validated_data, canSelectRoot):
        parent_id = validated_data.pop('parent')

        parent = None
        if parent_id == self.NO_PARENT and canSelectRoot:
            parent = self.Meta.model.get_root(assessment_id)
        elif parent_id > 0:
            checkParent = self.Meta.model.objects.filter(id=parent_id).first()
            if checkParent and checkParent.get_root(assessment_id).name == self.Meta.model.get_root_name(assessment_id):
                parent = checkParent

        return parent

    def create(self, validated_data):
        assessment = self.root.context['view'].assessment
        parent = self.get_parent(assessment.id, validated_data, canSelectRoot=False)
        parent_id = parent.id if parent else None

        return self.Meta.model.create_tag(
            assessment.id,
            parent_id=parent_id,
            **validated_data
        )

    def update(self, instance, validated_data):
        assessment = self.root.context['view'].assessment
        parent = self.get_parent(assessment.id, validated_data, canSelectRoot=True)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # check the following before moving:
        #   1) parent exists
        #   2) parent != self
        #   3) new parent != old parent
        #   4) new parent != descendant of self
        if parent and \
                instance.id != parent.id and  \
                parent.id != instance.get_parent().id and \
                parent.id not in instance.get_descendants().values_list('id', flat=True):

            instance.move(parent, pos='last-child')

        return instance
