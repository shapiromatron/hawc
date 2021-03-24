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
    ReadWriteSerializerMixin,
)
from ..common.api.viewsets import PermCheckerMixin
from ..common.helper import FlatExport, find_matching_list_element_value_by_value, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from . import exports, models, serializers
from .actions.model_metadata import EpiAssessmentMetadata, EpiMetadata


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

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def process_criteria_association(self, serializer, study_population_id, post_initial_create):
        """
        Associates/disassociates criteria of different categories (inclusion, exclusion, confounding)
        with the study population.
        """
        inserts = []
        spc_ids_to_disassociate = []

        # loop through each category; for each figure out what's currently saved on the studypop and
        # look at what id's were passed in.
        # from that we can determine what actual deletions/insertions need to be made, and batch those up
        # so we hit the db once for the deletes, and once for the inserts, and only if it's really needed.
        for data_key, type_code in self.criteria_categories:
            if data_key in self.request.data:
                # make a copy so we don't alter the contents of the initial request
                criteria_ids_to_create_for_type = [x for x in self.request.data[data_key]]

                if not post_initial_create:
                    existing_study_pop_criteria_for_type = models.StudyPopulationCriteria.objects.filter(
                        study_population=self.get_object(), criteria_type=type_code
                    )

                    for existing_study_pop_criteria in existing_study_pop_criteria_for_type:
                        existing_criteria = existing_study_pop_criteria.criteria

                        if existing_criteria.id in criteria_ids_to_create_for_type:
                            # the id is in the request but already associated; we don't need to re-insert it
                            criteria_ids_to_create_for_type.remove(existing_criteria.id)
                        else:
                            # the id is in the database but NOT in the request; we need to delete it
                            spc_ids_to_disassociate.append(existing_study_pop_criteria.id)

                # now - criteria_ids_to_create_for_type either contains all the ids (if during a create)
                # or just the ones that weren't removed b/c they are already in the db. We can now
                # build up just the inserts that actually need to happen.
                for criteria_id in criteria_ids_to_create_for_type:
                    dynamic_obj = {
                        "criteria_type": type_code,
                        "criteria": criteria_id,
                        "study_population": study_population_id,
                    }
                    inserts.append(dynamic_obj)

        # now that we've looked at each category we can hit the db.

        # wipe out existing criteria for each StudyPopulationCriteria.id that acutally needs deleting
        if len(spc_ids_to_disassociate) > 0:
            models.StudyPopulationCriteria.objects.filter(id__in=spc_ids_to_disassociate).delete()

        # ...and save any new ones
        if len(inserts) > 0:
            serializer = serializers.SimpleStudyPopulationCriteriaSerializer(
                data=inserts, many=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def handle_criteria(self, study_population):
        """
        Converts criteria input to id's; creating if necessary.
        """
        # first - what assessment are we working in?
        assessment_id = study_population.get_assessment().id

        # and now do some conversions/creations
        for cc in self.criteria_categories:
            data_key = cc[0]

            # client can supply an id, or the name of the criteria entry (and then we'll look it up for them - or create it if needed)
            if data_key in self.request.data:
                data_probe = self.request.data[data_key]

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

                self.request.data[data_key] = fixed

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.handle_criteria(serializer.instance)
        self.process_criteria_association(serializer, serializer.instance.id, True)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.handle_criteria(serializer.instance)
        self.process_criteria_association(serializer, serializer.instance.id, False)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
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
    read_serializer_class = serializers.ExposureSerializer
    write_serializer_class = serializers.ExposureWriteSerializer

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
        self.handle_metric_unit(request)
        self.handle_dtxsid(request)

        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
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

    def process_ct_creation(self, exposure, during_update):
        if during_update:
            # delete the existing ct's associated with this exposure; since we don't require CT id's to be passed in
            # this is the only good way to do this.
            models.CentralTendency.objects.filter(exposure=exposure).delete()

        # if a user is updating and doesn't supply a "central_tendencies" node, we just leave the previously saved CT's alone
        missing_needed_cts = not during_update

        cts = []

        if "central_tendencies" in self.request.data:
            missing_needed_cts = True

            cts = self.request.data["central_tendencies"]

            if len(cts) > 0:
                missing_needed_cts = False

                # populate each ct with the just created/updated exposure id
                for ct in cts:
                    ct["exposure"] = exposure.id

        if missing_needed_cts:
            raise ValidationError(f"At least one central tendency is required")
        elif len(cts) > 0:
            ct_serializer = serializers.CentralTendencySerializer(data=cts, many=True)
            ct_serializer.is_valid(raise_exception=True)
            ct_serializer.save()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.process_ct_creation(serializer.instance, False)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.process_ct_creation(serializer.instance, True)


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
        for data_key, is_included in self.factor_categories:
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


class Metadata(viewsets.ViewSet):
    def list(self, request):
        return EpiMetadata.handle_request(request)

    def retrieve(self, request, *args, **kwargs):
        assessment_id = kwargs["pk"]
        try:
            assessment = Assessment.objects.get(id=assessment_id)

            if assessment.user_can_view_object(request.user):
                eam = EpiAssessmentMetadata(None)
                return eam.handle_assessment_request(request, assessment)
            else:
                raise PermissionDenied("Invalid permission to view assessment metadata")
        except ObjectDoesNotExist:
            raise ValidationError("Invalid assessment id")
