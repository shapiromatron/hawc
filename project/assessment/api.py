from django.apps import apps
from django.core.urlresolvers import reverse
from django.db.models import Count

from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from . import models, serializers
from utils.helper import tryParseInt


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Please provide an `assessment_id` argument to your GET request.'


class DisabledPagination(PageNumberPagination):
    page_size = None


class AssessmentLevelPermissions(permissions.BasePermission):

    list_actions = ['list', ]

    def has_object_permission(self, request, view, obj):
        view.assessment = obj.get_assessment()
        if request.method in permissions.SAFE_METHODS:
            return view.assessment.user_can_view_object(request.user)
        elif obj == view.assessment:
            return view.assessment.user_can_edit_assessment(request.user)
        else:
            return view.assessment.user_can_edit_object(request.user)

    def has_permission(self, request, view):
        if view.action in self.list_actions:
            assessment_id = tryParseInt(request.GET.get('assessment_id'))
            if assessment_id is None:
                raise RequiresAssessmentID

            view.assessment = models.Assessment.objects\
                .filter(id=assessment_id)\
                .first()

            if view.assessment is None:
                return False

            return view.assessment.user_can_view_object(request.user)

        return True


class InAssessmentFilter(filters.BaseFilterBackend):
    """
    Filter objects which are in a particular assessment.

    Requires AssessmentLevelPermissions to set assessment
    """
    def filter_queryset(self, request, queryset, view):
        if view.action != 'list':
            return queryset

        filters = {view.assessment_filter_args: view.assessment.id}
        return queryset.filter(**filters)


class AssessmentViewset(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions, )
    filter_backends = (InAssessmentFilter, )

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentEditViewset(viewsets.ModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions, )
    parent_model = models.Assessment

    def get_queryset(self):
        return self.model.objects.all()


class DoseUnitsViewset(viewsets.ReadOnlyModelViewSet):
    model = models.DoseUnits
    serializer_class = serializers.DoseUnitsSerializer
    pagination_class = DisabledPagination

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentEndpointList(AssessmentViewset):
    serializer_class = serializers.AssessmentEndpointSerializer
    assessment_filter_args = "id"
    model = models.Assessment
    pagination_class = DisabledPagination

    def list(self, request, *args, **kwargs):
        """
        List has been optimized for queryset speed; some counts in get_queryset
        and others in the list here; depends on if a "select distinct" is
        required which significantly decreases query speed.
        """

        instance = self.filter_queryset(self.get_queryset())[0]
        app_url = reverse('assessment:clean_extracted_data', kwargs={'pk': instance.id})
        instance.items = []

        # animal
        instance.items.append({
            'count': instance.endpoint_count,
            'title': "animal bioassay endpoints",
            'type': 'ani',
            'url': "{}{}".format(app_url, 'ani/'),
        })
        count = apps.get_model('animal', 'Experiment')\
            .objects\
            .filter(study__assessment=instance.id)\
            .count()
        instance.items.append({
            "count": count,
            "title": "animal bioassay experiments",
            'type': 'experiment',
            'url': "{}{}".format(app_url, 'experiment/'),
        })
        count = apps.get_model('animal', 'AnimalGroup')\
            .objects\
            .filter(experiment__study__assessment=instance.id)\
            .count()
        instance.items.append({
            "count": count,
            "title": "animal bioassay animal groups",
            'type': 'animal-groups',
            'url': "{}{}".format(app_url, 'animal-groups/'),
        })

        # epi
        instance.items.append({
            "count": instance.outcome_count,
            "title": "epidemiological outcomes assessed",
            'type': 'epi',
            'url': "{}{}".format(app_url, 'epi/')
        })

        # in vitro
        instance.items.append({
            "count": instance.ivendpoint_count,
            "title": "in vitro endpoints",
            'type': 'in-vitro',
            'url': "{}{}".format(app_url, 'in-vitro/'),
        })
        count = apps.get_model('invitro', 'ivchemical')\
            .objects\
            .filter(study__assessment=instance.id)\
            .count()
        instance.items.append({
            "count": count,
            "title": "in vitro chemicals",
            'type': 'in-vitro-chemical',
            'url': "{}{}".format(app_url, 'in-vitro-chemical/'),
        })

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        id_ = tryParseInt(self.request.GET.get('assessment_id'))
        queryset = self.model.objects\
            .filter(id=id_)\
            .annotate(endpoint_count=Count('baseendpoint__endpoint'))\
            .annotate(outcome_count=Count('baseendpoint__outcome'))\
            .annotate(ivendpoint_count=Count('baseendpoint__ivendpoint'))
        return queryset
