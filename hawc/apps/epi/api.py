from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from ..assessment.api import AssessmentEditViewset, AssessmentLevelPermissions
from ..assessment.models import Assessment, DSSTox
from ..assessment.serializers import AssessmentSerializer
from ..common.api import (
    CleanupFieldsBaseViewSet,
    LegacyAssessmentAdapterMixin,
    ReadWriteSerializerMixin,
)
from ..common.api.viewsets import EditPermissionsCheckMixin
from ..common.helper import FlatExport, re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import HeatmapQuerySerializer, UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from . import exports, models, serializers
from .actions.model_metadata import EpiAssessmentMetadata


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

    @action(detail=True, url_path="export", renderer_classes=PandasRenderers)
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
            df = models.Result.heatmap_df(self.assessment.id, published_only=not unpublished)
            cache.set(key, df, settings.CACHE_1_HR)
        export = FlatExport(df=df, filename=f"epi-result-heatmap-{self.assessment.id}")
        return Response(export)


class Criteria(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["assessment"]
    assessment_filter_args = "assessment"
    model = models.Criteria
    serializer_class = serializers.CriteriaSerializer


class StudyPopulation(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer

    criteria_categories = (
        (
            "inclusion_criteria",
            "I",
        ),
        (
            "exclusion_criteria",
            "E",
        ),
        (
            "confounding_criteria",
            "C",
        ),
    )

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def process_criteria_association(self, serializer, study_population_id, post_initial_create):
        """
        Associates/disassociates criteria of different categories with the study population

        Loops through categories (inclusion, exclusion, confounding) and for each compares what's in the
        db with what's in the request; builds up a list of inserts/deletes to execute.

        Args:
            serializer: the serializer just used to create/update the study population
            study_population_id (int): the id of the study population that was just created/updated
            post_initial_create (bool): True if just after a create; False if just after an update
        """
        inserts = []
        spc_ids_to_disassociate = []

        # Loop through each category; for each figure out what's currently saved on the studypop and
        # look at what id's were passed in.
        # From that we can determine what actual deletions/insertions need to be made, and batch those up
        # so we hit the db once for the deletes, and once for the inserts, and only if it's really needed.
        for data_key, type_code in self.criteria_categories:
            if data_key in self.request.data:
                # Make a copy so we don't alter the contents of the initial request
                criteria_ids_to_create_for_type = [x for x in self.request.data[data_key]]

                if not post_initial_create:
                    existing_study_pop_criteria_for_type = (
                        models.StudyPopulationCriteria.objects.filter(
                            study_population=self.get_object(), criteria_type=type_code
                        )
                    )

                    for existing_study_pop_criteria in existing_study_pop_criteria_for_type:
                        existing_criteria = existing_study_pop_criteria.criteria

                        if existing_criteria.id in criteria_ids_to_create_for_type:
                            # The id is in the request but already associated; we don't need to re-insert it
                            criteria_ids_to_create_for_type.remove(existing_criteria.id)
                        else:
                            # The id is in the database but NOT in the request; we need to delete it
                            spc_ids_to_disassociate.append(existing_study_pop_criteria.id)

                # Now - criteria_ids_to_create_for_type either contains all the ids (if during a create)
                # or just the ones that weren't removed b/c they are already in the db. We can now
                # build up just the inserts that actually need to happen.
                for criteria_id in criteria_ids_to_create_for_type:
                    dynamic_obj = {
                        "criteria_type": type_code,
                        "criteria": criteria_id,
                        "study_population": study_population_id,
                    }
                    inserts.append(dynamic_obj)

        # Now that we've looked at each category we can hit the db.

        # Wipe out existing criteria for each StudyPopulationCriteria.id that acutally needs deleting
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

        Args:
            study_population (StudyPopulation): the just created StudyPopulation
        """
        assessment_id = study_population.get_assessment().id

        # Do some conversions/creations
        for cc in self.criteria_categories:
            data_key = cc[0]

            # Client can supply an id, or the name of the criteria entry (and then we'll look it up for them - or create it if needed)
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
                            # Allow creation of criteria as part of the request
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
        # Default behavior except we need to refresh the serializer to get the criteria to show up in the return...
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer.instance.refresh_from_db()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Exposure(ReadWriteSerializerMixin, EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["study_population"]
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    read_serializer_class = serializers.ExposureSerializer
    write_serializer_class = serializers.ExposureWriteSerializer

    def handle_dtxsid(self, request):
        """
        Calls get_or_create for DSSTox to ensure that the appropriate DXXTox exists in the db.
        """
        if "dtxsid" in request.data:
            dtxsid_probe = request.data["dtxsid"]
            try:
                DSSTox.objects.get_or_create(dtxsid=dtxsid_probe)
            except ValueError:
                raise ValidationError(
                    f"dtxsid '{dtxsid_probe}' does not exist and could not be imported"
                )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.handle_dtxsid(request)

        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.handle_dtxsid(request)

        # Default behavior except we need to refresh the serializer to get the central tendencies to show up in the return...
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Refresh serializer instance, as we want to get the central tendencies we created...
        serializer.instance.refresh_from_db()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def process_ct_creation(self, exposure, post_initial_create):
        """
        Creates/removes central tendencies as needed following exposure saves.

        Args:
            exposure (Exposure): the exposure that was just created/updated
            post_initial_create (bool): True if just after a create; False if just after an update

        """
        if not post_initial_create:
            # Delete the existing ct's associated with this exposure; since we don't require CT id's to be passed in
            # this is the only good way I could come up with to do this.
            models.CentralTendency.objects.filter(exposure=exposure).delete()

        # If a user is updating and doesn't supply a "central_tendencies" node, we just leave the previously saved CT's alone
        missing_needed_cts = post_initial_create

        cts = []

        if "central_tendencies" in self.request.data:
            missing_needed_cts = True

            cts = self.request.data["central_tendencies"]

            if cts is not None and len(cts) > 0:
                missing_needed_cts = False

                # Populate each ct with the just created/updated exposure id
                for ct in cts:
                    ct["exposure"] = exposure.id

        if missing_needed_cts:
            raise ValidationError("At least one central tendency is required")
        elif len(cts) > 0:
            ct_serializer = serializers.CentralTendencySerializer(data=cts, many=True)
            ct_serializer.is_valid(raise_exception=True)
            ct_serializer.save()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.process_ct_creation(serializer.instance, True)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.process_ct_creation(serializer.instance, False)


class Outcome(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["assessment", "study_population"]
    assessment_filter_args = "assessment"
    model = models.Outcome
    serializer_class = serializers.OutcomeSerializer


class GroupResult(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["group"]
    assessment_filter_args = "result__outcome__assessment"
    model = models.GroupResult
    serializer_class = serializers.GroupResultSerializer


class Result(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["outcome", "comparison_set"]
    assessment_filter_args = "outcome__assessment"
    model = models.Result
    serializer_class = serializers.ResultSerializer

    factor_categories = (
        (
            "factors_applied",
            True,
        ),
        (
            "factors_considered",
            False,
        ),
    )

    def process_adjustment_factor_association(self, serializer, result_id, post_initial_create):
        """
        Associates/disassociates adjustment factors of different categories with the result

        Loops through categories (included, considered) and for each compares what's in the
        db with what's in the request; builds up a list of inserts/deletes to execute.

        Args:
            serializer: the serializer just used to create/update the result
            result_id (int): the id of the result that was just created/updated
            post_initial_create (bool): True if just after a create; False if just after an update
        """
        inserts = []
        raf_ids_to_disassociate = []

        # See process_criteria_association; algorithm here is essentially identical.
        for data_key, is_included in self.factor_categories:
            if data_key in self.request.data:
                # Make a copy so we don't alter the contents of the initial request
                af_ids_to_create_for_type = [x for x in self.request.data[data_key]]

                if not post_initial_create:
                    existing_result_afs_for_type = models.ResultAdjustmentFactor.objects.filter(
                        result=self.get_object(), included_in_final_model=is_included
                    )

                    for existing_result_af in existing_result_afs_for_type:
                        existing_af = existing_result_af.adjustment_factor

                        if existing_af.id in af_ids_to_create_for_type:
                            # The id is in the request but already associated; we don't need to re-insert it
                            af_ids_to_create_for_type.remove(existing_af.id)
                        else:
                            # The id is in the database but NOT in the request; we need to delete it
                            raf_ids_to_disassociate.append(existing_result_af.id)

                # Now - af_ids_to_create_for_type either contains all the ids (if during a create)
                # or just the ones that weren't removed b/c they are already in the db. We can now
                # build up just the inserts that actually need to happen.
                for adjustment_factor_id in af_ids_to_create_for_type:
                    dynamic_obj = {
                        "included_in_final_model": is_included,
                        "adjustment_factor": adjustment_factor_id,
                        "result": result_id,
                    }
                    inserts.append(dynamic_obj)

        # Now that we've looked at each category we can hit the db.

        # Wipe out existing criteria for each ResultAdjustmentFactor.id that acutally needs deleting
        if len(raf_ids_to_disassociate) > 0:
            models.ResultAdjustmentFactor.objects.filter(id__in=raf_ids_to_disassociate).delete()

        # ...and save any new ones
        if len(inserts) > 0:
            serializer = serializers.SimpleResultAdjustmentFactorSerializer(data=inserts, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def handle_adjustment_factors(self, result):
        """
        Converts adjustment factor input to id's; creating if necessary.

        Args:
            result (Result): the just created result
        """
        assessment_id = result.get_assessment().id

        # Now do some conversions/creations
        for fc in self.factor_categories:
            data_key = fc[0]

            # Client can supply an id, or the name of the factor entry (and then we'll look it up for them - or create it if needed)
            if data_key in self.request.data:
                data_probe = self.request.data[data_key]

                fixed = []
                for el in data_probe:
                    if type(el) is str:
                        try:
                            adj_factor = models.AdjustmentFactor.objects.get(
                                description=el, assessment_id=assessment_id
                            )
                            fixed.append(adj_factor.id)
                        except ObjectDoesNotExist:
                            # Allow creation of adjustment factors as part of the request
                            af_serializer = serializers.AdjustmentFactorSerializer(
                                data={"description": el, "assessment": assessment_id}
                            )
                            af_serializer.is_valid(raise_exception=True)
                            af = af_serializer.save()
                            fixed.append(af.id)
                    else:
                        fixed.append(el)

                self.request.data[data_key] = fixed

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Default behavior except we need to refresh the serializer to get the adjustment factors to show up in the return...
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer.instance.refresh_from_db()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.handle_adjustment_factors(serializer.instance)
        self.process_adjustment_factor_association(serializer, serializer.instance.id, True)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.handle_adjustment_factors(serializer.instance)
        self.process_adjustment_factor_association(serializer, serializer.instance.id, False)


class ComparisonSet(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["study_population", "outcome"]
    assessment_filter_args = "assessment"  # todo: fix
    model = models.ComparisonSet
    serializer_class = serializers.ComparisonSetSerializer


class GroupNumericalDescriptions(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["group"]
    # assessment_filter_args = "group__assessment"
    model = models.GroupNumericalDescriptions
    serializer_class = serializers.GroupNumericalDescriptionsSerializer


class Group(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["comparison_set"]
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


class Metadata(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    model = Assessment
    serializer_class = AssessmentSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        if assessment.user_can_view_object(request.user):
            eam = EpiAssessmentMetadata(None)
            return eam.handle_assessment_request(request, assessment)
        else:
            raise PermissionDenied("Invalid permission to view assessment metadata")
