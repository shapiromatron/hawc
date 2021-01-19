from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

# from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.serializers import ValidationError

from ..assessment.api import (
    AssessmentLevelPermissions,
    AssessmentEditViewset,
    AssessmentViewset,
    InAssessmentFilter,
)
from ..assessment.models import Assessment
from ..common.api import (
    CleanupFieldsBaseViewSet,
    LegacyAssessmentAdapterMixin,
    ReadWriteSerializerMixin,
)
from ..common.helper import FlatExport, re_digits, tryParseInt
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from ..study.models import Study
from ..study.serializers import StudySerializer
from . import exports, models, serializers


class EpiAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = models.Outcome
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    @action(detail=True, methods=("get",), url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        """
        Retrieve epidemiology data for assessment.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        exporter = exports.OutcomeComplete(self.get_queryset(), filename=f"{self.assessment}-epi")
        return Response(exporter.build_export())

    @action(detail=True, url_path="study-heatmap", renderer_classes=PandasRenderers)
    def study_heatmap(self, request, pk):
        """
        Return heatmap data for assessment, at the study level (one row per study).

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_part_of_team(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-epi-study-heatmap-pub-{unpublished}"
        df = cache.get(key)
        if df is None:
            df = models.Result.heatmap_study_df(self.assessment, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"epi-study-heatmap-{self.assessment.id}")
        return Response(export)

    @action(detail=True, url_path="result-heatmap", renderer_classes=PandasRenderers)
    def result_heatmap(self, request, pk):
        """
        Return heatmap data for assessment, at the result level (one row per result).

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = HeatmapQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        unpublished = ser.data["unpublished"]
        if unpublished and not self.assessment.user_is_part_of_team(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        key = f"assessment-{self.assessment.id}-epi-result-heatmap-pub-{unpublished}"
        df = cache.get(key)
        if df is None:
            df = models.Result.heatmap_df(self.assessment, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"epi-result-heatmap-{self.assessment.id}")
        return Response(export)


# def lookup_existing_entity(data, id_field_name, model_class, serializer_class):
# probe_id = tryParseInt(data.get(id_field_name), -1)
# print(f"probe is is {probe_id}")
#
# try:
# entity = model_class.objects.get(id=probe_id)
# print(f"probe entity is {entity}")
# except ObjectDoesNotExist:
# print(f"error here")
# return None
# raise ValidationError("Invalid id")

# TODO - this code proabbyl belongs in the serializer - like "get raw representation" or something, rather than us manually de-readabling coi...
# serialized_entity = serializer_class().to_representation(entity)
# print(f"serialized entity is {serialized_entity}")
# return serialized_entity

# THINGS TO REVIEW WITH ANDY
# 1. general get_or_create approach
# 2. method of checking permissions - mixin + custom serializer helper method
# 3. looking at edit, not create, for permissions
# 4. the copythrough of study_id when creating study pops
# 5. for e.g. Outcome.diagnostic -- should client/user pass in <5> or "hospital admission"? -- ANSWER FROM ANDY: should be 5.


class Criteria(viewsets.ModelViewSet):
    assessment_filter_args = "assessment"
    model = models.Criteria
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter,)  # DjangoFilterBackend)
    serializer_class = serializers.CriteriaSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def create(self, request, *args, **kwargs):
        # note - this could be a list of criteria OR a single criteria, either will work
        criteria = request.data

        serializer = self.get_serializer(data=criteria, many=isinstance(criteria, list))
        serializer.is_valid(raise_exception=True)
        serializer.custom_perm_checker(request.user)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_207_MULTI_STATUS, headers=headers)


# TODO - check permissions here as well
class StudyPopulation(viewsets.ModelViewSet):
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def create(self, request, *args, **kwargs):
        pops = request.data.get("populations")
        # this one is being written to assume populations is a list; should
        # we actually assert/check that it is?

        study_id = tryParseInt(request.data.get("study_id"), -1)
        try:
            study = Study.objects.get(id=study_id)
        except ObjectDoesNotExist:
            raise ValidationError("Invalid study_id")
        # print(f"study is {study}")

        # TODO - do we need to check the permissions of the study?

        serialized_study = StudySerializer().to_default_representation(study)

        # print(f"serialized study is {serialized_study}")

        # for each population in the input, add the study
        for pop in pops:
            pop["study"] = serialized_study
            # pop["study"] = study.id

        # similarly - do we need to do this with criteria id's, outcome id's, etc.? Seems
        # like no, see epiUpload.json for an exmaple (it may not work, haven't gotten
        # that far yet)

        for pop in pops:
            raw_countries = pop.get("countries", [])
            real_countries = []
            for raw_country in raw_countries:
                print(f"lookup {raw_country}")
                country_id = tryParseInt(raw_country, -1)
                try:
                    country = models.Country.objects.get(id=country_id)
                    print(f"{country_id} --> {country}")
                    real_countries.append(
                        serializers.CountrySerializer().to_representation(country)
                    )
                    print(
                        f"FULL REP IS {serializers.CountrySerializer().to_representation(country)}"
                    )
                except ObjectDoesNotExist:
                    raise ValidationError("Invalid country_id")
            pop["countries"] = real_countries

        # serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer = self.get_serializer(data=pops, many=True)
        print(f"XXX: serializer is [{type(serializer)}]")

        serializer.is_valid(raise_exception=True)
        print(f"YYY: past our valid check")

        """
        print("CCC")
        self.perform_create(serializer)
        print("DDD")
        headers = self.get_success_headers(serializer.data)
        print("EEE")
        print(headers)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        """

        """
        study_id = tryParseInt(request.data.get("study_id"), -1)

        print(f"create firing with {study_id}")

        try:
            study = Study.objects.get(id=study_id)
        except ObjectDoesNotExist:
            raise ValidationError("Invalid study_id")

        # permission check using the user submitting the request
        if not study.user_can_edit_study(study.assessment, request.user):
            raise PermissionDenied(
                f"Submitter '{request.user}' has invalid permissions to edit Epi data for this study"
            )
        """

        """
        # overridden_objects is not marked as optional in RiskOfBiasScoreSerializerSlim; if it's not present
        # in the payload, let's just add an empty array.
        scores = request.data.get("scores")
        for score in scores:
            if "overridden_objects" not in score:
                score["overridden_objects"] = []
        """

        print(f"about to call create with {args}, {kwargs}...")

        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"exception: {e}")


class Exposure(AssessmentViewset):
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    serializer_class = serializers.ExposureSerializer


class Outcome(ReadWriteSerializerMixin, AssessmentEditViewset):
    assessment_filter_args = "assessment"
    model = models.Outcome
    read_serializer_class = serializers.OutcomeReadSerializer
    write_serializer_class = serializers.OutcomeWriteSerializer

    def create(self, request, *args, **kwargs):
        outcomes = request.data

        serializer = self.get_serializer(data=outcomes, many=isinstance(outcomes, list))
        serializer.is_valid(raise_exception=True)
        serializer.custom_perm_checker(request.user)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_207_MULTI_STATUS, headers=headers)


class Result(AssessmentViewset):
    assessment_filter_args = "outcome__assessment"
    model = models.Result
    serializer_class = serializers.ResultSerializer


class ComparisonSet(AssessmentViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.ComparisonSet
    serializer_class = serializers.ComparisonSetSerializer


class Group(AssessmentViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.Group
    serializer_class = serializers.GroupSerializer


class OutcomeCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.OutcomeCleanupFieldsSerializer
    model = models.Outcome
    assessment_filter_args = "assessment"


class StudyPopulationCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.StudyPopulationCleanupFieldsSerializer
    model = models.StudyPopulation
    assessment_filter_args = "study__assessment"


class ExposureCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ExposureCleanupFieldsSerializer
    model = models.Exposure
    assessment_filter_args = "study_population__study__assessment"
