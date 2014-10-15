from rest_framework import serializers

from myuser.models import HAWCUser
from assessment.models import Assessment
from lit.models import Reference
from study.models import Study
from animal.models import (Experiment, Species, Strain,
                           DosingRegime, DoseUnits, DoseGroup,
                           AnimalGroup, GenerationalAnimalGroup,
                           Endpoint, EndpointGroup, Aggregation)
from taggit.models import Tag

""" Users """
class HAWCUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HAWCUser
        fields = ('first_name', 'last_name', 'email')


""" Assessment """
class AssessmentSerializer(serializers.HyperlinkedModelSerializer):
    hawc_name = serializers.CharField(source='__unicode__')
    hawc_url = serializers.HyperlinkedIdentityField(view_name='assessment:detail', format='html')

    study = serializers.ManyHyperlinkedRelatedField(
        source='references',
        view_name='study-detail')

    aggregations = serializers.HyperlinkedRelatedField(
        read_only=True,
        many = True,
        source='aggregation',
        view_name='aggregation-detail')

    class Meta:
        model = Assessment


""" Literature """
class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference


""" Study """
class StudySerializer(serializers.HyperlinkedModelSerializer):
    hawc_url = serializers.HyperlinkedIdentityField(view_name='study:detail', format='html')
    experiment = serializers.ManyHyperlinkedRelatedField(
        source='experiments',
        view_name='experiment-detail')

    class Meta:
        model = Study
        fields = ('short_citation', 'hawc_url', 'experiment',
                  'study_populations', 'summary', 'full_citation', 'abstract')



""" Animal """
class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    hawc_name = serializers.CharField(source='__unicode__')
    hawc_url = serializers.HyperlinkedIdentityField(view_name='animal:experiment_detail', format='html')
    animal_group = serializers.ManyHyperlinkedRelatedField(
        source='animalgroup_set',
        view_name='animalgroup-detail')

    class Meta:
        model = Experiment


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Species
        fields = ('id', 'name')


class StrainSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Strain
        fields = ('id', 'name')


class DoseUnitsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DoseUnits
        fields = ('id', 'units')


class DoseGroupSerializer(serializers.HyperlinkedModelSerializer):
    dose_units = DoseUnitsSerializer()

    class Meta:
        model = DoseGroup
        fields = ('id', 'dose_group_id', 'dose', 'dose_units')


class DosingRegimeSerializer(serializers.HyperlinkedModelSerializer):
    dosed_animals = serializers.HyperlinkedRelatedField(
        source='dosed_animals',
        view_name='animalgroup-detail')
    doses = DoseGroupSerializer()

    class Meta:
        model = DosingRegime
        fields = ('id', 'dosed_animals', 'route_of_exposure',
                  'description', 'doses')


class GenerationalAnimalGroupSerializer(serializers.HyperlinkedModelSerializer):
    parents = serializers.ManyHyperlinkedRelatedField(
        source='parents',
        view_name='animalgroup-detail')

    class Meta:
        model = GenerationalAnimalGroup
        fields = ('id', 'generation', 'parents')


class AnimalGroupSerializer(serializers.HyperlinkedModelSerializer):
    hawc_name = serializers.CharField(source='__unicode__')
    hawc_url = serializers.HyperlinkedIdentityField(view_name='animal:animal_group_detail', format='html')
    experiment = serializers.HyperlinkedRelatedField(
        source='experiment',
        view_name='experiment-detail')
    species = SpeciesSerializer()
    strain = StrainSerializer()
    dosing_regime = DosingRegimeSerializer()
    endpoint = serializers.ManyHyperlinkedRelatedField(
        source='endpoint_set',
        view_name='endpoint-detail')
    generationalanimalgroup = GenerationalAnimalGroupSerializer()

    class Meta:
        model = AnimalGroup


class EndpointGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EndpointGroup
        fields = ('dose_group_id', 'n', 'incidence', 'response', 'variance')


class EndpointTagSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', )


class EndpointSerializer(serializers.HyperlinkedModelSerializer):
    hawc_name = serializers.CharField(source='__unicode__')
    hawc_url = serializers.HyperlinkedIdentityField(view_name='animal:endpoint_detail', format='html')
    endpoint_groups = EndpointGroupSerializer()
    effects = EndpointTagSerializer()
    animal_group = serializers.HyperlinkedRelatedField(
        source='animal_group',
        view_name='animalgroup-detail')

    class Meta:
        model = Endpoint
        fields = ('hawc_name', 'hawc_url', 'url', 'name', 'created', 'changed',
                  'animal_group', 'effects', 'response_units', 'data_type', 'NOAEL',
                  'LOAEL', 'endpoint_groups')
        depth = 1


class AggregationSerializer(serializers.HyperlinkedModelSerializer):
    hawc_name = serializers.CharField(source='__unicode__')
    hawc_url = serializers.HyperlinkedIdentityField(view_name='animal:aggregation_detail', format='html')
    assessment = serializers.HyperlinkedRelatedField(
        source='assessment',
        view_name='assessment-detail')
    dose_units = DoseUnitsSerializer()
    endpoints = EndpointSerializer()

    class Meta:
        model = Aggregation
