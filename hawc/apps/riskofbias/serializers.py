from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from rest_framework import serializers

from ..assessment.serializers import AssessmentMiniSerializer
from ..common.helper import SerializerHelper, tryParseInt
from ..myuser.models import HAWCUser
from ..myuser.serializers import HAWCUserSerializer
from ..study.models import Study
from . import constants, models


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


class SimpleRiskOfBiasDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasDomain
        fields = ("id", "name", "description", "is_overall_confidence")


class SimpleRiskOfBiasMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasMetric
        fields = ("id", "name", "description", "domain_id")


class RiskOfBiasAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasAssessment
        fields = "__all__"


class AssessmentRiskOfBiasSerializer(serializers.Serializer):
    assessment_id = serializers.IntegerField(source="id")
    domains = SimpleRiskOfBiasDomainSerializer(source="rob_domains", many=True)
    metrics = serializers.SerializerMethodField("get_metrics")
    rob_settings = RiskOfBiasAssessmentSerializer()
    score_metadata = serializers.SerializerMethodField("get_score_metadata")

    def get_metrics(self, instance):
        metrics = models.RiskOfBiasMetric.objects.filter(domain__assessment=instance)
        serializer = SimpleRiskOfBiasMetricSerializer(metrics, many=True)
        return serializer.data

    def get_score_metadata(self, instance):
        return {
            "choices": constants.SCORE_CHOICES_MAP,
            "symbols": constants.SCORE_SYMBOLS,
            "colors": constants.SCORE_SHADES,
            "bias_direction": {k: v for k, v in constants.BiasDirections.choices},
        }


class RiskOfBiasDomainSerializer(serializers.ModelSerializer):
    assessment = AssessmentMiniSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasDomain
        fields = "__all__"


class RiskOfBiasMetricSerializer(serializers.ModelSerializer):
    domain = RiskOfBiasDomainSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["response_values"] = instance.get_response_values()
        return ret

    class Meta:
        model = models.RiskOfBiasMetric
        fields = "__all__"


class RiskOfBiasScoreOverrideObjectSerializer(serializers.ModelSerializer):
    object_url = serializers.URLField(source="get_object_url", read_only=True)
    object_name = serializers.CharField(source="get_object_name", read_only=True)
    content_type_name = serializers.CharField(source="get_content_type_name")

    class Meta:
        model = models.RiskOfBiasScoreOverrideObject
        fields = ("id", "score_id", "content_type_name", "object_id", "object_name", "object_url")


class RiskOfBiasScoreCleanupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskOfBiasScore
        fields = (
            "id",
            "score",
            "notes",
        )


class AssessmentScoreSerializer(serializers.ModelSerializer):
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
            "metric_id",
            "overridden_objects",
            "riskofbias_id",
        )


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
        ret["bias_direction_description"] = instance.get_bias_direction_display()
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
            riskofbias=validated_data["riskofbias"],
            metric=validated_data["metric"],
            is_default=False,
            label="",
        )
        return override


class RiskOfBiasSerializer(serializers.ModelSerializer):
    scores = RiskOfBiasScoreSerializer(many=True)
    author = HAWCUserSerializer(read_only=True)

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
        is_create = self.instance is None

        if is_create:
            # convert study_id to Study object
            study_id = tryParseInt(self.initial_data["study_id"], -1)
            study = Study.objects.get(id=study_id)
            data["study"] = study

            # convert author_id to user
            author_id = tryParseInt(self.initial_data["author_id"], -1)
            author = None
            try:
                author = HAWCUser.objects.get(id=author_id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Invalid author_id")

            data["author"] = author

            assessment = study.assessment
            # we also checked permissions for the caller, not just the supplied author, in api.py
            if not study.user_can_edit_study(assessment, author):
                # author is the user specified by the "author_id" value in the payload
                raise serializers.ValidationError(
                    f"Author '{author}' has invalid permissions to edit Risk of Bias for this study"
                )

            # Validation should check that:
            # (1) no other active=True, final=True exists for this study_id, and
            # (2) for scores, a default=True exists for each required metric (by study type) for a study.

            # (1) does the study already have an active=True/final=True rob?
            if self.initial_data["active"] is True and self.initial_data["final"] is True:
                if study.riskofbiases.filter(active=True, final=True).exists():
                    raise serializers.ValidationError(
                        f"create failed; study {study_id} already has an active & final risk of bias"
                    )

            # (2) subject to the settings of the metrics defined for this assessment,
            # and the study_type of the study, we need to make sure all necessary scores
            # have been submitted with a default=True
            scores = self.initial_data["scores"]
            required_metrics = models.RiskOfBiasMetric.objects.get_required_metrics(
                assessment, study
            )
            problematic_scores = []
            for metric in required_metrics:
                domain = metric.domain
                # there could be multiple scores for a given metric if there are overrides, so we need to fetch them all
                scores_for_metric = [
                    score
                    for score in scores
                    if "metric_id" in score and score["metric_id"] == metric.id
                ]

                metric_descriptor = f"'{domain.name}:{metric.name}'"

                if len(scores_for_metric) == 0:
                    problematic_scores.append(
                        f"No score for metric {metric.id}/{metric_descriptor} was submitted"
                    )
                else:
                    num_defaults = len(
                        [score for score in scores_for_metric if score["is_default"] is True]
                    )
                    if num_defaults == 0:
                        problematic_scores.append(
                            f"No default score for metric {metric.id}/{metric_descriptor} was submitted."
                        )
                    elif num_defaults > 1:
                        problematic_scores.append(
                            f"Multiple default scores for metric {metric.id}/{metric_descriptor} were submitted."
                        )

            if len(problematic_scores) > 0:
                explanation = "; ".join(problematic_scores)
                raise serializers.ValidationError(
                    f"create failed; study {study_id} had problematic scores ({explanation})"
                )

            # store the actual metric object we want to create
            metrics_dict = {obj.id: obj for obj in required_metrics}
            for score, initial_score in zip(data["scores"], scores):
                score["metric"] = metrics_dict[initial_score["metric_id"]]

            override_options = models.RiskOfBias(study=study).get_override_options()
        else:
            score_ids = [score["id"] for score in self.initial_data["scores"]]

            if models.RiskOfBiasScore.objects.filter(
                id__in=score_ids, riskofbias=self.instance
            ).count() != len(score_ids):
                raise serializers.ValidationError("Cannot update; scores to not match instances")

            for initial_score_data, update_score in zip(
                self.initial_data["scores"], data["scores"]
            ):
                update_score["id"] = initial_score_data["id"]

            override_options = self.instance.get_override_options()

        # check overrides
        for key, values in override_options.items():
            override_options[key] = set(el[0] for el in values)

        # add cache to prevent lookups
        content_types = {}

        for initial_score_data, update_score in zip(self.initial_data["scores"], data["scores"]):
            overridden_objects = []
            if "overridden_objects" in initial_score_data:
                for obj in initial_score_data["overridden_objects"]:
                    ct_name = obj["content_type_name"]
                    object_id = obj["object_id"]

                    if ct_name not in override_options:
                        raise serializers.ValidationError(f"Invalid content type name: {ct_name}")

                    if object_id not in override_options[ct_name]:
                        raise serializers.ValidationError(
                            f"Invalid content object: {ct_name}: {object_id}"
                        )

                    if ct_name not in content_types:
                        app_label, model = ct_name.split(".")
                        content_types[ct_name] = ContentType.objects.get(
                            app_label=app_label, model=model
                        ).id

                    overridden_objects.append(
                        models.RiskOfBiasScoreOverrideObject(
                            # if it's an update we can use the id; else we'll insert it later after the score is saved
                            score_id=update_score["id"] if "id" in update_score else None,
                            content_type_id=content_types[ct_name],
                            object_id=object_id,
                        )
                    )

            update_score["overridden_objects"] = overridden_objects

        return data

    @transaction.atomic
    def create(self, validated_data):

        rob = models.RiskOfBias.objects.create(
            study=validated_data["study"],
            final=validated_data["final"],
            author=validated_data["author"],
            active=validated_data["active"],
        )

        scores_to_create = validated_data["scores"]
        for score_to_create in scores_to_create:
            try:
                score = models.RiskOfBiasScore.objects.create(
                    riskofbias=rob,
                    metric=score_to_create["metric"],
                    is_default=score_to_create["is_default"],
                    label=score_to_create["label"],
                    score=score_to_create["score"],
                    notes=score_to_create["notes"],
                )
            except ValidationError as err:
                raise serializers.ValidationError(err.message)

            overridden_objects = score_to_create["overridden_objects"]
            for overridden_object in overridden_objects:
                overridden_object.score = score
                overridden_object.save()

        return rob

    @transaction.atomic
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
            for score in models.RiskOfBiasScore.objects.filter(id__in=ids).prefetch_related(
                "overridden_objects"
            )
        }
        for update_score in update_scores:
            score = scores[update_score["id"]]
            for key in ["score", "label", "bias_direction", "notes"]:
                setattr(score, key, update_score[key])
            try:
                score.save()
            except ValidationError as err:
                raise serializers.ValidationError(err.message)

        # update overrides
        new_overrides = []
        for update_score in update_scores:
            new_overrides.extend(update_score["overridden_objects"])
        models.RiskOfBiasScoreOverrideObject.objects.filter(
            score__riskofbias_id=instance.id
        ).delete()
        models.RiskOfBiasScoreOverrideObject.objects.bulk_create(new_overrides)

        return super().update(instance, validated_data)


class SimpleRiskOfBiasSerializer(RiskOfBiasSerializer):
    scores = AssessmentScoreSerializer(many=True)


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
