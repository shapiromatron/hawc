import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db import transaction
from django.db.models import Case, Count, Q, Value, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    CleanupFieldsBaseViewSet,
    InAssessmentFilter,
    get_assessment_from_query,
)
from ..assessment.constants import AssessmentViewSetPermissions, PublishedStatus
from ..common.api import DisabledPagination
from ..common.helper import FlatExport, re_digits
from ..common.renderers import PandasRenderers
from ..common.views import create_object_log
from ..lit.constants import ReferenceDatabase
from ..lit.models import Reference
from ..riskofbias.serializers import RiskOfBiasSerializer
from . import filterset, models, serializers


class Study(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = "assessment"
    model = models.Study
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    list_actions = ["list", "rob_scores"]
    lookup_value_regex = re_digits

    def get_serializer_class(self):
        if self.action == "create_from_identifier":
            return serializers.StudyFromIdentifierSerializer
        elif self.action in ["list", "create"]:
            return serializers.SimpleStudySerializer
        else:
            return serializers.VerboseStudySerializer

    def get_queryset(self):
        if self.action == "list":
            if not self.assessment.user_can_edit_object(self.request.user):
                return self.model.objects.published(self.assessment)
            return self.model.objects.get_qs(self.assessment)
        else:
            return self.model.objects.prefetch_related(
                "identifiers",
                "riskofbiases__scores__overridden_objects__content_object",
            ).select_related("assessment")

    @action(detail=False, action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def rob_scores(self, request):
        scores = self.model.objects.rob_scores(self.assessment.pk)
        return Response(scores)

    @action(detail=False, permission_classes=[])
    def types(self, request):
        study_types = self.model.STUDY_TYPE_FIELDS
        return Response(study_types)

    def create(self, request):
        # permissions check not here; see serializer validation
        return super().create(request)

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        create_object_log(
            "Created",
            serializer.instance,
            serializer.instance.get_assessment().id,
            self.request.user.id,
        )

    @action(
        detail=True,
        url_path="all-rob",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
    )
    def rob(self, request, pk: int):
        study = self.get_object()
        serializer = RiskOfBiasSerializer(study.get_active_robs(), many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=("post",), url_path="create-from-identifier", permission_classes=[]
    )
    def create_from_identifier(self, request):
        # check permissions
        assessment = get_assessment_from_query(request)
        if not assessment.user_can_edit_object(request.user):
            raise PermissionDenied()
        # validate and create
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        renderer_classes=PandasRenderers,
        permission_classes=(permissions.IsAdminUser,),
    )
    def chemical(self, request):
        """Global search by chemical, across all studies."""
        fs = filterset.StudyByChemicalFilterSet(request.GET, queryset=self.get_queryset())
        model_fields = [
            "id",
            "title",
            "authors_short",
            "pmid",
            "hero",
            "doi",
            "assessment",
            "assessment__name",
            "assessment__dtxsids",
            "assessment__cas",
            "published",
            "study",
            "study__short_citation",
            "study__published",
            "num_robs",
            "study__bioassay",
            "study__epi",
            "study__epi_meta",
            "study__in_vitro",
            "study__eco",
            "num_tags",
            "num_user_tags",
        ]
        column_names = [
            "HAWC ID",
            "Title",
            "Authors",
            "PubMed IDs",
            "HERO IDs",
            "DOIs",
            "Assessment ID",
            "Assessment Name",
            "Assessment DTXSIDs",
            "Assessment CAS",
            "Assessment Published",
            "Study ID",
            "Study Citation",
            "Study Published",
            "Study Risk of Bias Analysis Count",
            "Study Bioassay",
            "Study Epidemiological",
            "Study Epi/Meta",
            "Study In Vitro",
            "Study Ecology",
            "Reference Tags Count",
            "Reference User Tags Count",
        ]
        qs = (
            Reference.objects.filter(id__in=fs.qs)
            .select_related("study", "assessment")
            .prefetch_related("identifiers", "tags", "user_tags")
            .annotate(
                num_tags=Count("tags"),
                num_user_tags=Count("user_tags", filter=Q(user_tags__is_resolved=False)),
                num_robs=Count("study__riskofbiases"),
                pmid=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.PUBMED),
                    delimiter="|",
                    distinct=True,
                    default="",
                ),
                hero=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.HERO),
                    delimiter="|",
                    distinct=True,
                    default="",
                ),
                doi=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.DOI),
                    delimiter="|",
                    distinct=True,
                    default="",
                ),
                assessment__dtxsids=StringAgg("assessment__dtxsids", delimiter=", ", distinct=True),
                published=Case(
                    When(assessment__public_on__isnull=True, then=Value(PublishedStatus.PRIVATE)),
                    When(
                        Q(assessment__public_on__isnull=False)
                        & Q(assessment__hide_from_public_page=False),
                        then=Value(PublishedStatus.PUBLIC),
                    ),
                    When(
                        Q(assessment__public_on__isnull=False)
                        & Q(assessment__hide_from_public_page=True),
                        then=Value(PublishedStatus.UNLISTED),
                    ),
                ),
            )
            .values_list(*model_fields)
        )
        df = pd.DataFrame(list(qs), columns=column_names)
        export = FlatExport(
            df=df,
            filename=f"global-study-data-{request.GET.get('query')}",
        )
        return Response(export)


class StudyCleanupFieldsView(CleanupFieldsBaseViewSet):
    model = models.Study
    serializer_class = serializers.StudyCleanupFieldsSerializer
    assessment_filter_args = "assessment"
