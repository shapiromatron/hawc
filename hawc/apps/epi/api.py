from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from django.db import transaction
from django.db.models import Q
# from rest_framework import status, viewsets
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from ..assessment.api import AssessmentEditViewset, AssessmentLevelPermissions, AssessmentViewset
from ..assessment.models import Assessment, DoseUnits, DSSTox
from ..assessment.serializers import DoseUnitsSerializer, DSSToxSerializer
from ..common.api import (
    CleanupFieldsBaseViewSet,
    LegacyAssessmentAdapterMixin,
    ReadWriteSerializerMixin,
    user_can_edit_object,
)
from ..common.helper import FlatExport, re_digits, tryParseInt, find_matching_list_element_by_value
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from ..study.models import Study
from ..study.serializers import StudySerializer
from . import exports, models, serializers

from hawc.services.epa.dsstox import DssSubstance


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


class Criteria(AssessmentEditViewset):
    assessment_filter_args = "assessment"
    model = models.Criteria
    serializer_class = serializers.CriteriaSerializer

    def perform_create(self, serializer):
        # permissions check
        user_can_edit_object(
            serializer.validated_data.get("assessment"), self.request.user, raise_exception=True
        )
        return super().perform_create(serializer)


class StudyPopulation(viewsets.ModelViewSet):
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def create(self, request, *args, **kwargs):
        # IGNORE THIS FOR NOW - NOT REALLY WORKING YET, JUST PLAYING WITH SOME IDEAS

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


class Exposure(ReadWriteSerializerMixin, AssessmentEditViewset):
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    read_serializer_class = serializers.ExposureReadSerializer
    write_serializer_class = serializers.ExposureWriteSerializer

    def handle_cts(self, request, during_update = False):
        """
        a bit of an overly big hammer -- during an update we just wipe out existing CTs. We could instead load existing ones, delete if missing,
        update if present, etc. but for simplicity's sake this works.
        """
        if during_update:
            models.CentralTendency.objects.filter(exposure=self.get_object()).delete()

        # we validate CTs here...and then post-exposure creation, we'll create them.
        if "central_tendencies" in request.data:
            cts = request.data["central_tendencies"]

            # allow clients to specify either keys like 2 or readable values like "median" when accessing the API
            for ct in cts:
                if "estimate_type" in ct:
                    probe_ct_estimate_type = ct["estimate_type"]
                    if type(probe_ct_estimate_type) is str:
                        converted_estimate_type = find_matching_list_element_by_value(models.CentralTendency.ESTIMATE_TYPE_CHOICES, probe_ct_estimate_type, False)
                        if converted_estimate_type is None:
                            raise ValidationError(f"Invalid estimate_type value '{probe_ct_estimate_type}'")
                        else:
                            ct["estimate_type"] = converted_estimate_type

                if "variance_type" in ct:
                    probe_ct_variance_type = ct["variance_type"]
                    if type(probe_ct_variance_type) is str:
                        converted_variance_type = find_matching_list_element_by_value(models.CentralTendency.VARIANCE_TYPE_CHOICES, probe_ct_variance_type)
                        if converted_variance_type is None:
                            raise ValidationError(f"Invalid variance_type value '{probe_ct_variance_type}'")
                        else:
                            ct["variance_type"] = converted_variance_type

            # raise ValidationError("FORCE ERRO")

            ct_serializer = serializers.CentralTendencyPreviewSerializer(
                data=cts, many=True
            )
            try:
                ct_serializer.is_valid(raise_exception=True)
            except ValidationError as ve:
                raise ValidationError({
                    "central_tendencies": ve.detail
                })

    def handle_dtxsid(self, request):
        # supports creating dsstox objects on the fly
        if "dtxsid" in request.data:
            dtxsid_probe = request.data["dtxsid"]
            try:
                dtxsid = DSSTox.objects.get(dtxsid=dtxsid_probe)
            except ObjectDoesNotExist:
                try:
                    substance = DssSubstance.create_from_dtxsid(dtxsid_probe)

                    dsstox = DSSTox(dtxsid=substance.dtxsid, content=substance.content)
                    dsstox.save()
                except ValueError as err:
                    raise ValidationError(f"dtxsid '{dtxsid_probe}' does not exist and could not be imported")

    def handle_metric_unit(self, request):
        # client can supply an id, or the name of the doseunits entry (and then we'll look it up for them - or create it if needed)
        if "metric_units" in request.data:
            metric_units_probe = request.data["metric_units"]

            if type(metric_units_probe) is str:
                try:
                    metric_units = DoseUnits.objects.get(name=metric_units_probe)
                    request.data["metric_units"] = metric_units.id
                except ObjectDoesNotExist:
                    # option 1 - require a pre-existing dose unit
                    # raise ValidationError(f"metric_units lookup value '{metric_units_probe}' could not be resolved")

                    # option 2 - allow creation of metric_units as part of the request
                    du_serializer = DoseUnitsSerializer(
                        data={"name": metric_units_probe }
                    )
                    du_serializer.is_valid(raise_exception=True)
                    metric_units = du_serializer.save()
                    request.data["metric_units"] = metric_units.id
        # else leave it alone

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.handle_cts(request, True)
        self.handle_metric_unit(request)
        self.handle_dtxsid(request)

        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.handle_cts(request, False)
        self.handle_metric_unit(request)
        self.handle_dtxsid(request)

        # default behavior except we need to refresh the serializer to get the central tendencies to show up in the return...
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # refresh serializer instance, as we want to get the central tendencies we created...
        instance = self.model.objects.get(id=serializer.data["id"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def process_ct_creation(self, serializer, exposure_id):
        if "central_tendencies" in self.request.data:
            cts = self.request.data["central_tendencies"]
            for ct in cts:
                ct["exposure"] = exposure_id

            ct_serializer = serializers.CentralTendencyWriteSerializer(
                data=cts, many=True
            )
            ct_serializer.is_valid(raise_exception=True)
            ct_serializer.save()
        
    def perform_create(self, serializer):
        user_can_edit_object(
            serializer.validated_data.get("study_population"),
            self.request.user,
            raise_exception=True,
        )
        super().perform_create(serializer)

        self.process_ct_creation(serializer, serializer.data["id"])

    def perform_update(self, serializer):
        user_can_edit_object(
            serializer.validated_data.get("study_population"),
            self.request.user,
            raise_exception=True,
        )
        super().perform_update(serializer)

        self.process_ct_creation(serializer, self.get_object().id)


class Outcome(ReadWriteSerializerMixin, AssessmentEditViewset):
    assessment_filter_args = "assessment"
    model = models.Outcome
    read_serializer_class = serializers.OutcomeReadSerializer
    write_serializer_class = serializers.OutcomeWriteSerializer

    def perform_create(self, serializer):
        # permissions check
        user_can_edit_object(
            serializer.validated_data.get("assessment"), self.request.user, raise_exception=True
        )
        return super().perform_create(serializer)


class Result(ReadWriteSerializerMixin, AssessmentEditViewset):
    assessment_filter_args = "outcome__assessment"
    model = models.Result
    read_serializer_class = serializers.ResultReadSerializer
    write_serializer_class = serializers.ResultWriteSerializer

    def handle_mapped_choices(self, request):
        if "metric" in request.data:
            probe_metric = request.data["metric"]

            if type(probe_metric) is str:
                try:
                    metric = models.ResultMetric.objects.get(Q(metric__iexact=probe_metric) | Q(abbreviation__iexact=probe_metric))
                    request.data["metric"] = metric.id
                except ObjectDoesNotExist:
                    raise ValidationError(f"metric lookup value '{probe_metric}' could not be resolved")

        fields_that_support_mapping = [
            ( "dose_response", models.Result.DOSE_RESPONSE_CHOICES ),
        ]

        for el in fields_that_support_mapping:
            key = el[0]
            mapping_data = el[1]

            if key in request.data:
                probe_val = request.data[key]

                if type(probe_val) is str:
                    converted_val = find_matching_list_element_by_value(mapping_data, probe_val)
                    if converted_val is None:
                        raise ValidationError(f"Invalid {key} value '{probe_val}'")
                    else:
                        request.data[key] = converted_val

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.handle_mapped_choices(request)
        default_response = super().create(request, *args, **kwargs)

        instance = self.model.objects.get(id=default_response.data["id"])
        serializer = self.read_serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.handle_mapped_choices(request)
        super().update(request, *args, **kwargs)

        serializer = self.read_serializer_class(self.get_object())
        return Response(serializer.data)


class ComparisonSet(AssessmentEditViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.ComparisonSet
    serializer_class = serializers.ComparisonSetSerializer


class GroupNumericalDescriptions(AssessmentEditViewset):
    # assessment_filter_args = "group__assessment"
    model = models.GroupNumericalDescriptions
    serializer_class = serializers.GroupNumericalDescriptionsSerializer


class Group(AssessmentEditViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.Group
    serializer_class = serializers.GroupSerializer

    def perform_create(self, serializer):
        user_can_edit_object(
            serializer.validated_data.get("comparison_set"),
            self.request.user,
            raise_exception=True,
        )
        super().perform_create(serializer)

    def perform_update(self, serializer):
        user_can_edit_object(
            self.get_object(),
            self.request.user,
            raise_exception=True,
        )
        super().perform_update(serializer)


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
