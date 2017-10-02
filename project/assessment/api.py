import logging

from django.apps import apps
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.db.models import Count

from rest_framework import permissions, status, viewsets, decorators, filters
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination

from . import models, serializers
from utils.helper import tryParseInt


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Please provide an `assessment_id` argument to your GET request.'


class DisabledPagination(PageNumberPagination):
    page_size = None


def get_assessment_from_query(request):
    """Returns assessment or None."""
    assessment_id = tryParseInt(request.GET.get('assessment_id'))
    if assessment_id is None:
        raise RequiresAssessmentID

    return models.Assessment.objects\
        .get_qs(assessment_id)\
        .first()


class AssessmentLevelPermissions(permissions.BasePermission):

    list_actions = ['list', ]

    def has_object_permission(self, request, view, obj):
        if not hasattr(view, 'assessment'):
            view.assessment = obj.get_assessment()
        if request.method in permissions.SAFE_METHODS:
            return view.assessment.user_can_view_object(request.user)
        elif obj == view.assessment:
            return view.assessment.user_can_edit_assessment(request.user)
        else:
            return view.assessment.user_can_edit_object(request.user)

    def has_permission(self, request, view):
        if view.action in self.list_actions:
            logging.info('Permission checked')

            if not hasattr(view, 'assessment'):
                view.assessment = get_assessment_from_query(request)

            if view.assessment is None:
                return False

            return view.assessment.user_can_view_object(request.user)

        return True


class InAssessmentFilter(filters.BaseFilterBackend):
    """
    Filter objects which are in a particular assessment.
    """
    def filter_queryset(self, request, queryset, view):
        list_actions = getattr(view, 'list_actions', ['list'])
        if view.action not in list_actions:
            return queryset

        if not hasattr(view, 'assessment'):
            view.assessment = get_assessment_from_query(request)

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
    filter_backends = (InAssessmentFilter, )

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentRootedTagTreeViewset(viewsets.ModelViewSet):
    """
    Base viewset used with utils/models/AssessmentRootedTagTree subclasses
    """
    permission_classes = (AssessmentLevelPermissions, )

    PROJECT_MANAGER = 'PROJECT_MANAGER'
    TEAM_MEMBER = 'TEAM_MEMBER'
    create_requires = TEAM_MEMBER

    def get_queryset(self):
        return self.model.objects.all()

    def list(self, request):
        self.filter_queryset(self.get_queryset())
        data = self.model.get_all_tags(self.assessment.id, json_encode=False)
        return Response(data)

    def create(self, request, *args, **kwargs):
        # get an assessment
        assessment_id = tryParseInt(request.data.get('assessment_id'), -1)
        self.assessment = models.Assessment.objects\
                .get_qs(assessment_id)\
                .first()
        if self.assessment is None:
            raise RequiresAssessmentID

        self.check_editing_permission(request)

        return super().create(request, *args, **kwargs)

    @decorators.detail_route(methods=('patch',))
    def move(self, request, *args, **kwargs):
        instance = self.get_object()
        self.assessment = instance.get_assessment()
        self.check_editing_permission(request)
        instance.moveWithinSiblingsToIndex(request.data['newIndex'])
        return Response({'status': True})

    def check_editing_permission(self, request):
        if self.create_requires == self.PROJECT_MANAGER:
            permissions_check = self.assessment.user_can_edit_assessment
        elif self.create_requires == self.TEAM_MEMBER:
            permissions_check = self.assessment.user_can_edit_object
        else:
            raise ValueError('invalid configuration of `create_requires`')

        if not permissions_check(request.user):
            raise exceptions.PermissionDenied()


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
            .get_qs(instance.id)\
            .count()
        instance.items.append({
            "count": count,
            "title": "animal bioassay experiments",
            'type': 'experiment',
            'url': "{}{}".format(app_url, 'experiment/'),
        })

        count = apps.get_model('animal', 'AnimalGroup')\
            .objects\
            .get_qs(instance.id)\
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
            .get_qs(instance.id)\
            .count()
        instance.items.append({
            "count": count,
            "title": "in vitro chemicals",
            'type': 'in-vitro-chemical',
            'url': "{}{}".format(app_url, 'in-vitro-chemical/'),
        })

        # study
        count = apps.get_model('study', 'Study')\
            .objects\
            .get_qs(instance.id)\
            .count()
        instance.items.append({
            "count": count,
            "title": "studies",
            "type": "study",
            "url": "{}{}".format(app_url, 'study/'),
            })

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        id_ = tryParseInt(self.request.GET.get('assessment_id'))
        queryset = self.model.objects\
            .get_qs(id_)\
            .annotate(endpoint_count=Count('baseendpoint__endpoint'))\
            .annotate(outcome_count=Count('baseendpoint__outcome'))\
            .annotate(ivendpoint_count=Count('baseendpoint__ivendpoint'))
        return queryset
