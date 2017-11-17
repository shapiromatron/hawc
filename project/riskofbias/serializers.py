from rest_framework import serializers

from assessment.serializers import AssessmentMiniSerializer
from utils.helper import SerializerHelper

from myuser.serializers import HAWCUserSerializer
from . import models


class AssessmentMetricChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasMetric
        fields = ('id', 'name', 'description')


class AssessmentMetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasMetric
        fields = '__all__'

class AssessmentMetricAnswersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.RiskOfBiasMetricAnswers
        fields = '__all__'


class AssessmentDomainSerializer(serializers.ModelSerializer):
    metrics = AssessmentMetricSerializer(many=True)

    class Meta:
        model = models.RiskOfBiasDomain
        fields = '__all__'


class RiskOfBiasDomainSerializer(serializers.ModelSerializer):
    assessment = AssessmentMiniSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasDomain
        fields = '__all__'


class RiskOfBiasMetricSerializer(serializers.ModelSerializer):
    domain = RiskOfBiasDomainSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasMetric
        fields = '__all__'


class RiskOfBiasMetricAnswersSerializer(serializers.ModelSerializer):
    metric = RiskOfBiasMetricSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBiasMetricAnswers
        fields = '__all__'


class RiskOfBiasAnswersRecordedSerializer(serializers.ModelSerializer):
    answers = RiskOfBiasMetricAnswersSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['recorded_score'] = instance.get_score_display
        ret['answer_choice'] = instance.riskofbiasmetricanswers.answer_choice
        ret['answer_symbol'] = instance.riskofbiasmetricanswers.answer_symbol
        ret['answer_shade'] = instance.riskofbiasmetricanswers.answer_shade
        ret['url_edit'] = instance.riskofbias.get_edit_url()
        ret['study_name'] = instance.riskofbias.study.short_citation
        ret['study_id'] = instance.riskofbias.study.id
        ret['study_types'] = instance.riskofbias.study.get_study_type()

    class Meta:
        model = models.RiskOfBiasAnswersRecorded
        fields = ('id', 'recorded_score', 'recorded_notes', 'answers')


class RiskOfBiasScoreSerializer(serializers.ModelSerializer):
    metric = RiskOfBiasMetricSerializer(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['score_description'] = instance.get_score_display()
        ret['score_symbol'] = instance.score_symbol
        ret['score_shade'] = instance.score_shade
        ret['url_edit'] = instance.riskofbias.get_edit_url()
        ret['study_name'] = instance.riskofbias.study.short_citation
        ret['study_id'] = instance.riskofbias.study.id
        ret['study_types'] = instance.riskofbias.study.get_study_type()
        return ret

    class Meta:
        model = models.RiskOfBiasScore
        fields = ('id', 'score', 'notes', 'metric')


class RiskOfBiasSerializer(serializers.ModelSerializer):
    scores = RiskOfBiasScoreSerializer(read_only=False, many=True, partial=True)
    author = HAWCUserSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBias
        fields = ('id', 'author', 'active',
                  'final', 'study', 'created',
                  'last_updated', 'scores')

    def update(self, instance, validated_data):
        """
        Updates the nested RiskOfBiasScores with submitted data before updating
        the RiskOfBias instance.
        """
        score_data = validated_data.pop('scores')
        for score, form_data in zip(instance.scores.all(), score_data):
            for field, value in list(form_data.items()):
                setattr(score, field, value)
            score.save()
        return super().update(instance, validated_data)

class RiskOfBiasCustomAnswersSerializer(serializers.ModelSerializer):
    recorded_answers = RiskOfBiasAnswersRecordedSerializer(read_only=False, many=True, partial=True)
    author = HAWCUserSerializer(read_only=True)

    class Meta:
        model = models.RiskOfBias
        fields = ('id', 'author', 'active',
                  'final', 'study', 'created',
                  'last_updated', 'recorded_answers')

    def update(self, instance, validated_data):
        """
        Updates the nested RiskOfBiasScores with submitted data before updating
        the RiskOfBias instance.
        """
        answers_data = validated_data.pop('record_scores')
        for recorded_answers, form_data in zip(instance.recorded_answers.all(), answers_data):
            for field, value in list(form_data.items()):
                setattr(recorded_answers, field, value)
            recorded_answers.save()
        return super().update(instance, validated_data)


class AssessmentMetricScoreSerializer(serializers.ModelSerializer):
    scores = serializers.SerializerMethodField('get_final_score')

    class Meta:
        model = models.RiskOfBiasMetric
        fields = ('id', 'name', 'description', 'scores')

    def get_final_score(self, instance):
        scores = instance.scores.filter(riskofbias__final=True, riskofbias__active=True)
        serializer = RiskOfBiasScoreSerializer(scores, many=True)
        return serializer.data


class AssessmentRiskOfBiasScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasScore
        fields = ('id', 'notes', 'score')

class AssessmentRiskOfBiasAnswersRecordedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiskOfBiasAnswersRecorded
        fields = ('id', 'recorded_score', 'recorded_notes')

SerializerHelper.add_serializer(models.RiskOfBias, RiskOfBiasSerializer)
