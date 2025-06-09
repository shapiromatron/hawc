from django.apps import apps
from django.db.models import Manager, Prefetch


class TermManager(Manager):
    def assessment_systems(self, assessment_id):
        Endpoint = apps.get_model("animal", "Endpoint")
        return (
            self.get_queryset()
            .filter(
                endpoint_system_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "endpoint_system_terms",
                    queryset=Endpoint.objects.filter(
                        animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
                    ),
                    to_attr="endpoints",
                )
            )
        )

    def assessment_organs(self, assessment_id):
        Endpoint = apps.get_model("animal", "Endpoint")
        return (
            self.get_queryset()
            .filter(
                endpoint_organ_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "endpoint_organ_terms",
                    queryset=Endpoint.objects.filter(
                        animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
                    ),
                    to_attr="endpoints",
                )
            )
        )

    def assessment_effects(self, assessment_id):
        Endpoint = apps.get_model("animal", "Endpoint")
        return (
            self.get_queryset()
            .filter(
                endpoint_effect_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "endpoint_effect_terms",
                    queryset=Endpoint.objects.filter(
                        animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
                    ),
                    to_attr="endpoints",
                )
            )
        )

    def assessment_effect_subtypes(self, assessment_id):
        Endpoint = apps.get_model("animal", "Endpoint")
        return (
            self.get_queryset()
            .filter(
                endpoint_effect_subtype_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "endpoint_effect_subtype_terms",
                    queryset=Endpoint.objects.filter(
                        animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
                    ),
                    to_attr="endpoints",
                )
            )
        )

    def assessment_endpoint_names(self, assessment_id):
        Endpoint = apps.get_model("animal", "Endpoint")
        return (
            self.get_queryset()
            .filter(
                endpoint_name_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
            )
            .distinct()
            .prefetch_related(
                Prefetch(
                    "endpoint_name_terms",
                    queryset=Endpoint.objects.filter(
                        animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
                    ),
                    to_attr="endpoints",
                )
            )
        )
