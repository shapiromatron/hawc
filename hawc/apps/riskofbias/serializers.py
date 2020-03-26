import datetime

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from ..assessment.serializers import AssessmentMiniSerializer
from ..common.helper import SerializerHelper, tryParseInt
from ..myuser.models import HAWCUser
from ..myuser.serializers import HAWCUserSerializer
from ..study.models import Study
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
            riskofbias=validated_data["riskofbias"],
            metric=validated_data["metric"],
            is_default=False,
            label="",
        )
        return override


class RiskOfBiasSerializer(serializers.ModelSerializer):
    scores = RiskOfBiasScoreSerializer(many=True)
    author = HAWCUserSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret[
            "rob_response_values"
        ] = instance.study.assessment.rob_settings.get_rob_response_values()
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
        if self.instance is not None: # ie, it's an update. When creating a new RoB, we don't have id's in the score
            score_ids = [score["id"] for score in self.initial_data["scores"]]
            if models.RiskOfBiasScore.objects.filter(
                id__in=score_ids, riskofbias=self.instance
            ).count() != len(score_ids):
                raise serializers.ValidationError("Cannot update; scores to not match instances")
            for initial_score_data, update_score in zip(self.initial_data["scores"], data["scores"]):
                update_score["id"] = initial_score_data["id"]

            # check overrides
            override_options = self.instance.get_override_options()
            for key, values in override_options.items():
                override_options[key] = set(el[0] for el in values)
        else:
            # creating a new RoB object
            # convert the supplied study_id to an actual Study object...
            study_id = tryParseInt(self.initial_data["study_id"], -1)
            study = Study.objects.get(id=study_id)
            if study is None:
                raise serializers.ValidationError("Invalid study_id")
            else:
                data["study"] = study


            # ...and same for author_id
            author_id = tryParseInt(self.initial_data["author_id"], -1)
            author = HAWCUser.objects.get(id=author_id)
            if author is None:
                raise serializers.ValidationError("Invalid author_id")
            else:
                data["author"] = author

            assessment = study.assessment
            # we also checked permissions for the caller, not just the supplied author, in api.py
            if not study.user_can_edit_study(assessment, author):
                # author is the user specified by the "author_id" value in the payload
                raise serializers.ValidationError("Author '%s' has invalid permissions to edit Risk of Bias for this study" % author)


            # Validation should check that:
            # (1) no other active=True, final=True exists for this study_id, and
            # (2) for scores, a default=True exists for each required metric (by study type) for a study.

            # (1) does the study already have an active=True/final=True rob?
            robs = study.riskofbiases.all()
            for rob in robs:
                if rob.active and rob.final:
                    raise serializers.ValidationError("create failed; study %s already has an active & final risk of bias" % study_id)

            # study_type is an array like ['bioassay','epi']
            study_type = study.get_study_type()

            # (2) subject to the settings of the metrics defined for this assessment,
            # and the study_type of the study, we need to make sure all necessary scores
            # have been submitted with a default=True
            scores = self.initial_data["scores"]
            required_metrics = models.RiskOfBiasMetric.objects.get_required_metrics(assessment, study)
            problematic_scores = []
            for metric in required_metrics:
                domain = metric.domain
                submitted_score = next((score for score in scores if "metric_id" in score and score["metric_id"] == metric.id), None)

                metric_descriptor = "'%s:%s'" % (domain.name, metric.name)
                if submitted_score is None:
                    problematic_scores.append("No score for metric %s/%s was submitted" % (metric.id, metric_descriptor))
                elif "is_default" not in submitted_score or submitted_score["is_default"] != True:
                    problematic_scores.append("The score for metric %s/%s was submitted but not marked as default" % (metric.id, metric_descriptor))

            if len(problematic_scores) > 0:
                explanation = "; ".join(problematic_scores)
                raise serializers.ValidationError("create failed; study %s had problematic scores (%s)" % (study_id, explanation))

            # store the actual metric object we want to create
            score_idx = 0
            for score in data["scores"]:
                metric = models.RiskOfBiasMetric.objects.get(id=scores[score_idx]["metric_id"])
                # score["metric_id"] = scores[score_idx]["metric_id"]
                score["metric"] = metric
                score_idx += 1

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
                            score_id=update_score["id"],
                            content_type_id=content_types[ct_name],
                            object_id=object_id,
                        )
                    )

            update_score["overridden_objects"] = overridden_objects

        return data

    def create(self, validated_data):
        right_now = datetime.datetime.now()
        validated_data["created"] = right_now
        validated_data["last_updated"] = right_now

        # print(validated_data)

        rob = models.RiskOfBias.objects.create(
            study = validated_data["study"],
            final = validated_data["final"],
            author = validated_data["author"],
            active = validated_data["active"],
            created = validated_data["created"],
            last_updated = validated_data["last_updated"]
        )

        scores_to_create = validated_data["scores"]
        for score_to_create in scores_to_create:
            score = models.RiskOfBiasScore.objects.create(
                riskofbias = rob,
                metric = score_to_create["metric"],
                is_default = score_to_create["is_default"],
                label = score_to_create["label"],
                score = score_to_create["score"],
                notes = score_to_create["notes"]
            )

        return rob

        # TODO - do we need to handle overrides?
        """
        Creates the nested RiskOfBiasScores with submitted data before creating
        the RiskOfBias instance.
        """

        """
        for update_score in update_scores:
            score = scores[update_score["id"]]
            for key in ["score", "label", "notes"]:
                setattr(score, key, update_score[key])
            score.save()

        # update overrides
        new_overrides = []
        for update_score in update_scores:
            new_overrides.extend(update_score["overridden_objects"])
        models.RiskOfBiasScoreOverrideObject.objects.filter(
            score__riskofbias_id=instance.id
        ).delete()
        models.RiskOfBiasScoreOverrideObject.objects.bulk_create(new_overrides)

        return super().update(instance, validated_data)
        """

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
            for key in ["score", "label", "notes"]:
                setattr(score, key, update_score[key])
            score.save()

        # update overrides
        new_overrides = []
        for update_score in update_scores:
            new_overrides.extend(update_score["overridden_objects"])
        models.RiskOfBiasScoreOverrideObject.objects.filter(
            score__riskofbias_id=instance.id
        ).delete()
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
