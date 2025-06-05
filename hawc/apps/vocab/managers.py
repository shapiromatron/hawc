import json
from pathlib import Path

from django.apps import apps
from django.conf import settings
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


class GuidelineProfileManager(Manager):
    def get_guideline_choices(self) -> list:
        guidelines = self._load_guideline_data()
        choices = [
            (guideline["guideline_name"], guideline["guideline_name"]) for guideline in guidelines
        ]
        return choices

    def get_guideline_id(self, name) -> int:
        guidelines = self._load_guideline_data()
        if name:
            id = list(filter(lambda x: x["guideline_name"] == name, guidelines))[0]["guideline_id"]
            return int(id)
        return None

    def get_guideline_name(self, guideline_id) -> str:
        guidelines = self._load_guideline_data()
        name = list(filter(lambda x: x["guideline_id"] == f"{guideline_id}", guidelines))[0][
            "guideline_name"
        ]
        return name

    def _load_guideline_data(self) -> dict:
        """Return guideline fixture data."""
        p = Path(settings.PROJECT_PATH) / "apps/vocab/fixtures/guidelines.json"
        return json.loads(p.read_text())
