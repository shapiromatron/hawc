from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from ..assessment.serializers import AssessmentMiniSerializer
from ..common.helper import SerializerHelper
from ..myuser.serializers import HAWCUserSerializer
from . import models


class AssessmentMetricChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasMetric
        fields = ("id", "name", "description")


class AssessmentMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasMetric
        fields = "__all__"


class AssessmentDomainSerializer(serializers.ModelSerializer):
    metrics = AssessmentMetricSerializer(many=True)

    class Meta:
        model = models.RiskOfBiasDomain
        fields = "__all__"


class RiskOfBiasDomainSerializer(serializers.ModelSerializer):
    assessment = AssessmentMiniSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasDomain
        fields = "__all__"


class RiskOfBiasMetricSerializer(serializers.ModelSerializer):
    domain = RiskOfBiasDomainSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasMetric
        fields = "__all__"


class RiskOfBiasScoreOverrideObjectSerializer(serializers.ModelSerializer):
    object_url = serializers.URLField(source="get_object_url")
    object_name = serializers.CharField(source="get_object_name")
    content_type_name = serializers.CharField(source="get_content_type_name")

    class Meta:
        model = models.RiskOfBiasScoreOverrideObject
        fields = ("id", "score_id", "content_type_name", "object_id", "object_name", "object_url")


class RiskOfBiasScoreSerializerSlim(serializers.ModelSerializer):
    metric = RiskOfBiasMetricSerializer(read_only=True)
    overridden_objects = RiskOfBiasScoreOverrideObjectSerializer(many=True)

    class Meta:
        model = models.RiskOfBiasScore
        fields = (
            "id",
            "score",
            "is_default",
            "label",
            "bias_direction",
            "notes",
            "metric",
            "overridden_objects",
            "riskofbias_id",
        )


class RiskOfBiasScoreSerializer(RiskOfBiasScoreSerializerSlim):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["score_description"] = instance.get_score_display()
        ret["score_symbol"] = instance.score_symbol
        ret["score_shade"] = instance.score_shade
        ret["url_edit"] = instance.riskofbias.get_edit_url()
        ret["study_name"] = instance.riskofbias.study.short_citation
        ret["study_id"] = instance.riskofbias.study.id
        ret["study_types"] = instance.riskofbias.study.get_study_type()
        return ret


class RiskOfBiasScoreOverrideCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasScore
        fields = ("id", "riskofbias", "metric")

    def create(self, validated_data):
        override = models.RiskOfBiasScore.objects.create(
            riskofbias=validated_data["riskofbias"], metric=validated_data["metric"], is_default=False, label="",
        )
        return override


class RiskOfBiasSerializer(serializers.ModelSerializer):
    scores = RiskOfBiasScoreSerializer(many=True)
    author = HAWCUserSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["rob_response_values"] = instance.study.assessment.rob_settings.get_rob_response_values()
        return ret

    class Meta:
        model = models.RiskOfBias
        fields = (
            "id",
            "author",
            "active",
            "final",
            "study",
            "created",
            "last_updated",
            "scores",
        )
        read_only_fields = ("id", "study")

    def validate(self, data):

        # make sure that all scores match those in score; add `id` field to validated data
        score_ids = [score["id"] for score in self.initial_data["scores"]]
        if models.RiskOfBiasScore.objects.filter(id__in=score_ids, riskofbias=self.instance).count() != len(score_ids):
            raise serializers.ValidationError("Cannot update; scores to not match instances")
        for initial_score_data, update_score in zip(self.initial_data["scores"], data["scores"]):
            update_score["id"] = initial_score_data["id"]

        # check overrides
        override_options = self.instance.get_override_options()
        for key, values in override_options.items():
            override_options[key] = set(el[0] for el in values)

        # add cache to prevent lookups
        content_types = {}

        for initial_score_data, update_score in zip(self.initial_data["scores"], data["scores"]):
            overridden_objects = []
            for obj in initial_score_data["overridden_objects"]:
                ct_name = obj["content_type_name"]
                object_id = obj["object_id"]

                if ct_name not in override_options:
                    raise serializers.ValidationError(f"Invalid content type name: {ct_name}")

                if object_id not in override_options[ct_name]:
                    raise serializers.ValidationError(f"Invalid content object: {ct_name}: {object_id}")

                if ct_name not in content_types:
                    app_label, model = ct_name.split(".")
                    content_types[ct_name] = ContentType.objects.get(app_label=app_label, model=model).id

                overridden_objects.append(
                    models.RiskOfBiasScoreOverrideObject(
                        score_id=update_score["id"], content_type_id=content_types[ct_name], object_id=object_id,
                    )
                )

            update_score["overridden_objects"] = overridden_objects

        return data

    def update(self, instance, validated_data):
        """
        Updates the nested RiskOfBiasScores with submitted data before updating
        the RiskOfBias instance.
        """

        # update scores
        update_scores = validated_data.pop("scores")
        ids = [score["id"] for score in update_scores]
        scores = {
            score.id: score
            for score in models.RiskOfBiasScore.objects.filter(id__in=ids).prefetch_related("overridden_objects")
        }
        for update_score in update_scores:
            score = scores[update_score["id"]]
            for key in ["score", "label", "notes"]:
                setattr(score, key, update_score[key])
            score.save()

        # update overrides
        new_overrides = []
        for update_score in update_scores:
            new_overrides.extend(update_score["overridden_objects"])
        models.RiskOfBiasScoreOverrideObject.objects.filter(score__riskofbias_id=instance.id).delete()
        models.RiskOfBiasScoreOverrideObject.objects.bulk_create(new_overrides)

        return super().update(instance, validated_data)


class AssessmentMetricScoreSerializer(serializers.ModelSerializer):
    scores = serializers.SerializerMethodField("get_final_score")

    class Meta:
        model = models.RiskOfBiasMetric
        fields = ("id", "name", "description", "scores")

    def get_final_score(self, instance):
        scores = instance.scores.filter(riskofbias__final=True, riskofbias__active=True)
        serializer = RiskOfBiasScoreSerializer(scores, many=True)
        return serializer.data


SerializerHelper.add_serializer(models.RiskOfBias, RiskOfBiasSerializer)
