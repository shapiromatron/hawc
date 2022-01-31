from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from ..assessment.api import AssessmentEditViewset
from ..common.api.viewsets import EditPermissionsCheckMixin
from . import models, serializers


class Design(EditPermissionsCheckMixin, AssessmentEditViewset):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.Design
    serializer_class = serializers.DesignSerializer

    criteria_categories = (
        ("inclusion_criteria", "I",),
        ("exclusion_criteria", "E",),
        ("confounding_criteria", "C",),
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
                    existing_study_pop_criteria_for_type = models.DesignCriteria.objects.filter(
                        study_population=self.get_object(), criteria_type=type_code
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

        # Wipe out existing criteria for each DesignCriteria.id that acutally needs deleting
        if len(spc_ids_to_disassociate) > 0:
            models.DesignCriteria.objects.filter(id__in=spc_ids_to_disassociate).delete()

        # ...and save any new ones
        if len(inserts) > 0:
            serializer = serializers.SimpleDesignCriteriaSerializer(data=inserts, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def handle_criteria(self, study_population):
        """
        Converts criteria input to id's; creating if necessary.

        Args:
            study_population (Design): the just created Design
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
