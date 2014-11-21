
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from assessment.models import Assessment
from study.models import Study
from animal.models import Experiment, AnimalGroup, Endpoint, Aggregation
from myuser.models import HAWCUser

from . import permissions
from . import serializers


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': {
            'users': reverse('hawcuser-list', request=request),
            },
        'assessment': {
            'assessments': reverse('assessment-list', request=request),
            }
    })


""" User resources """
@permission_classes((IsAdminUser, ))
class HAWCUserList(generics.ListAPIView):
    model = HAWCUser
    serializer_class = serializers.HAWCUserSerializer


@permission_classes((IsAdminUser, ))
class HAWCUserDetail(generics.RetrieveAPIView):
    model = HAWCUser
    serializer_class = serializers.HAWCUserSerializer


""" Assessment resources """
class AssessmentList(generics.ListAPIView):
    model = Assessment
    serializer_class = serializers.AssessmentSerializer
    paginate_by = 10

    def get_queryset(self):
        """
        Filter by assessments a user has permission to view.
        """
        user = self.request.user
        assessments = Assessment.objects.all()
        return [assess for assess in assessments if assess.user_can_view_object(user)]


@permission_classes((permissions.AssessmentLevelPermissions, ))
class AssessmentDetail(generics.RetrieveAPIView):
    model = Assessment
    serializer_class = serializers.AssessmentSerializer


""" Study resources """
class StudyList(generics.ListAPIView):
    model = Study
    serializer_class = serializers.StudySerializer

    def get_queryset(self):
        return Study.objects.filter(assessment=self.kwargs.get('pk'))


@permission_classes((permissions.AssessmentLevelPermissions, ))
class StudyDetail(generics.RetrieveAPIView):
    model = Study
    serializer_class = serializers.StudySerializer


""" Endpoint resources """
class ExperimentList(generics.ListAPIView):
    model = Experiment
    serializer_class = serializers.ExperimentSerializer

    def get_queryset(self):
        return Experiment.objects.filter(study__in=
                    Study.objects.filter(assessment=self.kwargs.get('pk')))

@permission_classes((permissions.AssessmentLevelPermissions, ))
class ExperimentDetail(generics.RetrieveAPIView):
    model = Experiment
    serializer_class = serializers.ExperimentSerializer


class AnimalGroupList(generics.ListAPIView):
    model = AnimalGroup
    serializer_class = serializers.AnimalGroupSerializer

    def get_queryset(self):
        return AnimalGroup.objects.filter(experiment__in=
                    Experiment.objects.filter(study__in=
                        Study.objects.filter(assessment=self.kwargs.get('pk'))))

@permission_classes((permissions.AssessmentLevelPermissions, ))
class AnimalGroupDetail(generics.RetrieveAPIView):
    model = AnimalGroup
    serializer_class = serializers.AnimalGroupSerializer


class EndpointList(generics.ListAPIView):
    model = Endpoint
    serializer_class = serializers.EndpointSerializer

    def get_queryset(self):
        return Endpoint.objects.filter(animal_group__in=
                    AnimalGroup.objects.filter(experiment__in=
                    Experiment.objects.filter(study__in=
                    Study.objects.filter(assessment=self.kwargs.get('pk')))))


@permission_classes((permissions.AssessmentLevelPermissions, ))
class EndpointDetail(generics.RetrieveAPIView):
    model = Endpoint
    serializer_class = serializers.EndpointSerializer


class AggregationList(generics.ListAPIView):
    model = Aggregation
    serializer_class = serializers.AggregationSerializer

    def get_queryset(self):
        return Aggregation.objects.filter(assessment=self.kwargs.get('pk'))


@permission_classes((permissions.AssessmentLevelPermissions, ))
class AggregationDetail(generics.RetrieveAPIView):
    model = Aggregation
    serializer_class = serializers.AggregationSerializer
