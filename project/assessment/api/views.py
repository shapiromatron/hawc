import logging

from django.core import exceptions
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination

from assessment import models, serializers

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
            logging.info('Permission checked')

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
                .filter(id=assessment_id)\
                .first()
        if self.assessment is None:
            raise RequiresAssessmentID

        # ensure user can edit assessment
        if self.create_requires == self.PROJECT_MANAGER:
            permissions_check = self.assessment.user_can_edit_assessment
        elif self.create_requires == self.TEAM_MEMBER:
            permissions_check = self.assessment.user_can_edit_object
        else:
            raise ValueError('invalid configuration of `create_requires`')

        if not permissions_check(request.user):
            raise exceptions.PermissionDenied()

        return super(AssessmentRootedTagTreeViewset, self)\
            .create(request, *args, **kwargs)


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
