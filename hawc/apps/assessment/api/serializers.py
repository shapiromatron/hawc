from rest_framework import serializers


class AssessmentRootedSerializer(serializers.ModelSerializer):
    """
    Base serializer used with AssessmentRootedTagTree model.
    """

    NO_PARENT = -1

    def get_parent(self, assessment_id, validated_data, canSelectRoot):
        parent_id = validated_data.pop("parent", self.NO_PARENT)

        parent = None
        if parent_id == self.NO_PARENT and canSelectRoot:
            parent = self.Meta.model.get_assessment_root(assessment_id)
        elif parent_id > 0:
            checkParent = self.Meta.model.objects.filter(id=parent_id).first()
            if (
                checkParent
                and checkParent.get_root().name
                == self.Meta.model.get_assessment_root_name(assessment_id)
            ):
                parent = checkParent

        return parent

    def create(self, validated_data):
        parent = self.get_parent(self.assessment.id, validated_data, canSelectRoot=False)
        parent_id = parent.id if parent else None
        return self.Meta.model.create_tag(self.assessment.id, parent_id=parent_id, **validated_data)

    def update(self, instance, validated_data):
        assessment = self.instance.get_assessment()
        parent = self.get_parent(assessment.id, validated_data, canSelectRoot=True)

        for attr, value in list(validated_data.items()):
            setattr(instance, attr, value)
        instance.save()

        # check the following before moving:
        #   1) parent exists
        #   2) parent != self
        #   3) new parent != old parent
        #   4) new parent != descendant of self
        if (
            parent
            and instance.id != parent.id
            and parent.id != instance.get_parent().id
            and parent.id not in instance.get_descendants().values_list("id", flat=True)
        ):
            instance.move(parent, pos="last-child")

        return instance
