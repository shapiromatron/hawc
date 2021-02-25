from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from hawc.services.epa.dsstox import DssSubstance

from ..assessment.api import AssessmentEditViewset, AssessmentLevelPermissions
from ..assessment.models import Assessment, DoseUnits, DSSTox
from ..assessment.serializers import DoseUnitsSerializer
from ..common.api import (
    CleanupFieldsBaseViewSet,
    LegacyAssessmentAdapterMixin,
    PermCheckerMixin,
    ReadWriteSerializerMixin,
)
from ..common.helper import FlatExport, find_matching_list_element_by_value, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from ..study.models import Study
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


class Criteria(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = "assessment"
    assessment_filter_args = "assessment"
    model = models.Criteria
    serializer_class = serializers.CriteriaSerializer


class StudyPopulation(PermCheckerMixin, viewsets.ModelViewSet):
    perm_checker_key = "study"
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer

    criteria_categories = (
        ("inclusion_criteria", "I",),
        ("exclusion_criteria", "E",),
        ("confounding_criteria", "C",),
    )

    def process_criteria_association(self, serializer, study_population_id, post_initial_create):
        # this should probably be rewritten to use the ManyToManyManager on the underlying instance...
        inserts = []
        for cc in self.criteria_categories:
            data_key = cc[0]
            type_code = cc[1]

            if data_key in self.request.data:
                if not post_initial_create:
                    # wipe out existing criteria for this pop+type pair that was part of the request...
                    models.StudyPopulationCriteria.objects.filter(
                        study_population=self.get_object(), criteria_type=type_code
                    ).delete()

                criteria_ids = self.request.data[data_key]

                for criteria_id in criteria_ids:
                    dynamic_obj = {
                        "criteria_type": type_code,
                        "criteria": criteria_id,
                        "study_population": study_population_id,
                    }
                    inserts.append(dynamic_obj)

        # ...and save any new ones
        if len(inserts) > 0:
            serializer = serializers.SimpleStudyPopulationCriteriaSerializer(
                data=inserts, many=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def handle_criteria(self, request, during_create):
        # first - what assessment are we working in?
        assessment_id = None
        if during_create:
            if "study" in request.data:
                study_id = request.data["study"]

                try:
                    study = Study.objects.get(id=study_id)
                    assessment_id = study.get_assessment().id
                except ObjectDoesNotExist:
                    raise ValidationError({"study": "Invalid study id"})
            else:
                raise ValidationError({"study": "No study id supplied"})
        else:
            assessment_id = self.get_object().get_assessment().id

        if assessment_id is None:
            return

        # and now do some conversions/creations
        for cc in self.criteria_categories:
            data_key = cc[0]

            # client can supply an id, or the name of the criteria entry (and then we'll look it up for them - or create it if needed)
            if data_key in request.data:
                data_probe = request.data[data_key]

                fixed = []
                for el in data_probe:
                    if type(el) is str:
                        try:
                            criteria = models.Criteria.objects.get(
                                description=el, assessment_id=assessment_id
                            )
                            fixed.append(criteria.id)
                        except ObjectDoesNotExist:
                            # allow creation of criteria as part of the request
                            criteria_serializer = serializers.CriteriaSerializer(
                                data={"description": el, "assessment": assessment_id}
                            )
                            criteria_serializer.is_valid(raise_exception=True)
                            criteria = criteria_serializer.save()
                            fixed.append(criteria.id)
                    else:
                        fixed.append(el)

                request.data[data_key] = fixed

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.process_criteria_association(serializer, serializer.data["id"], True)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.process_criteria_association(serializer, self.get_object().id, False)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.handle_criteria(request, False)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.handle_criteria(request, True)
        # return super().create(request, *args, **kwargs)

        # default behavior except we need to refresh the serializer to get the criteria to show up in the return...
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        instance = self.model.objects.get(id=serializer.data["id"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Exposure(ReadWriteSerializerMixin, PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = "study_population"
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    read_serializer_class = serializers.SimpleExposureSerializer
    write_serializer_class = serializers.ExposureWriteSerializer

    def handle_cts(self, request, during_update=False):
        # we validate CTs here...and then post-exposure creation, we'll create them.
        if "central_tendencies" in request.data:
            """
            a bit of an overly big hammer -- during an update we just wipe out existing CTs. We could instead load existing ones, delete if missing,
            update if present, etc. but for simplicity's sake this works.
            """
            if during_update:
                models.CentralTendency.objects.filter(exposure=self.get_object()).delete()

            cts = request.data["central_tendencies"]

            if len(cts) == 0:
                raise ValidationError(f"At least one central tendency is required")

            # allow clients to specify either keys like 2 or readable values like "median" when accessing the API
            for ct in cts:
                if "estimate_type" in ct:
                    probe_ct_estimate_type = ct["estimate_type"]
                    if type(probe_ct_estimate_type) is str:
                        converted_estimate_type = find_matching_list_element_by_value(
                            models.CentralTendency.ESTIMATE_TYPE_CHOICES,
                            probe_ct_estimate_type,
                            False,
                        )
                        if converted_estimate_type is None:
                            raise ValidationError(
                                f"Invalid estimate_type value '{probe_ct_estimate_type}'"
                            )
                        else:
                            ct["estimate_type"] = converted_estimate_type

                if "variance_type" in ct:
                    probe_ct_variance_type = ct["variance_type"]
                    if type(probe_ct_variance_type) is str:
                        converted_variance_type = find_matching_list_element_by_value(
                            models.CentralTendency.VARIANCE_TYPE_CHOICES, probe_ct_variance_type
                        )
                        if converted_variance_type is None:
                            raise ValidationError(
                                f"Invalid variance_type value '{probe_ct_variance_type}'"
                            )
                        else:
                            ct["variance_type"] = converted_variance_type

            # raise ValidationError("FORCE ERRO")

            ct_serializer = serializers.CentralTendencyPreviewSerializer(data=cts, many=True)
            try:
                ct_serializer.is_valid(raise_exception=True)
            except ValidationError as ve:
                raise ValidationError({"central_tendencies": ve.detail})
        else:
            if not during_update:
                raise ValidationError(f"At least one central tendency is required")

    def handle_dtxsid(self, request):
        # supports creating dsstox objects on the fly
        if "dtxsid" in request.data:
            dtxsid_probe = request.data["dtxsid"]
            try:
                DSSTox.objects.get(dtxsid=dtxsid_probe)
            except ObjectDoesNotExist:
                try:
                    substance = DssSubstance.create_from_dtxsid(dtxsid_probe)

                    dsstox = DSSTox(dtxsid=substance.dtxsid, content=substance.content)
                    dsstox.save()
                except ValueError:
                    raise ValidationError(
                        f"dtxsid '{dtxsid_probe}' does not exist and could not be imported"
                    )

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
                    du_serializer = DoseUnitsSerializer(data={"name": metric_units_probe})
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

            ct_serializer = serializers.CentralTendencyWriteSerializer(data=cts, many=True)
            ct_serializer.is_valid(raise_exception=True)
            ct_serializer.save()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.process_ct_creation(serializer, serializer.data["id"])

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.process_ct_creation(serializer, self.get_object().id)


class Outcome(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = ["assessment", "study_population"]
    assessment_filter_args = "assessment"
    model = models.Outcome
    serializer_class = serializers.OutcomeSerializer


class GroupResult(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = "group"
    assessment_filter_args = "result__outcome__assessment"
    model = models.GroupResult
    serializer_class = serializers.GroupResultSerializer

    # note - this does not currently validate that a supplied group is part of the assessment.


class Result(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = ["outcome", "comparison_set"]
    assessment_filter_args = "outcome__assessment"
    model = models.Result
    serializer_class = serializers.ResultSerializer

    factor_categories = (("factors_applied", True,), ("factors_considered", False,))

    def process_adjustment_factor_creation(self, serializer, result_id, post_initial_create):
        inserts = []
        for fc in self.factor_categories:
            data_key = fc[0]
            is_included = fc[1]

            if data_key in self.request.data:
                if not post_initial_create:
                    # wipe out existing factors for this result+included_in_final_model pair that was part of the request...
                    models.ResultAdjustmentFactor.objects.filter(
                        result=self.get_object(), included_in_final_model=is_included
                    ).delete()

                adjustment_factor_ids = self.request.data[data_key]

                for adjustment_factor_id in adjustment_factor_ids:
                    dynamic_obj = {
                        "included_in_final_model": is_included,
                        "adjustment_factor": adjustment_factor_id,
                        "result": result_id,
                    }
                    inserts.append(dynamic_obj)

        # ...and save any new ones
        if len(inserts) > 0:
            serializer = serializers.SimpleResultAdjustmentFactorSerializer(data=inserts, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def handle_adjustment_factors(self, request, during_create):
        # first - what assessment are we working in?
        assessment_id = None
        if during_create:
            if "outcome" in request.data:
                outcome_id = request.data["outcome"]

                try:
                    outcome = models.Outcome.objects.get(id=outcome_id)
                    assessment_id = outcome.get_assessment().id
                except ObjectDoesNotExist:
                    raise ValidationError({"outcome": "Invalid outcome id supplied"})
            else:
                raise ValidationError({"outcome": "No outcome id supplied"})
        else:
            assessment_id = self.get_object().get_assessment().id

        # and now do some conversions/creations
        for fc in self.factor_categories:
            data_key = fc[0]

            # client can supply an id, or the name of the factor entry (and then we'll look it up for them - or create it if needed)
            if data_key in request.data:
                data_probe = request.data[data_key]

                fixed = []
                for el in data_probe:
                    if type(el) is str:
                        try:
                            adj_factor = models.AdjustmentFactor.objects.get(
                                description=el, assessment_id=assessment_id
                            )
                            fixed.append(adj_factor.id)
                        except ObjectDoesNotExist:
                            # allow creation of adjustment factors as part of the request
                            af_serializer = serializers.AdjustmentFactorSerializer(
                                data={"description": el, "assessment": assessment_id}
                            )
                            af_serializer.is_valid(raise_exception=True)
                            af = af_serializer.save()
                            fixed.append(af.id)
                    else:
                        fixed.append(el)

                request.data[data_key] = fixed

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.handle_adjustment_factors(request, False)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.handle_adjustment_factors(request, True)
        # return super().create(request, *args, **kwargs)

        # default behavior except we need to refresh the serializer to get the adjustment factors to show up in the return...
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        instance = self.model.objects.get(id=serializer.data["id"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.process_adjustment_factor_creation(serializer, serializer.data["id"], True)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.process_adjustment_factor_creation(serializer, self.get_object().id, False)


class ComparisonSet(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = "study_population"
    assessment_filter_args = "assessment"  # todo: fix
    model = models.ComparisonSet
    serializer_class = serializers.ComparisonSetSerializer

    # note - this does not currently validate that a supplied exposure is a valid one...


class GroupNumericalDescriptions(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = "group"
    # assessment_filter_args = "group__assessment"
    model = models.GroupNumericalDescriptions
    serializer_class = serializers.GroupNumericalDescriptionsSerializer


class Group(PermCheckerMixin, AssessmentEditViewset):
    perm_checker_key = "comparison_set"
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
