from typing import Any, Dict

import pytest

from hawc.apps.animal.serializers import DosingRegimeSerializer, ExperimentSerializer
from hawc.apps.assessment.models import DSSTox


@pytest.mark.django_db
class TestExperimentSerializer:
    def _get_valid_dataset(self, db_keys):
        data: Dict[str, Any] = dict(
            study_id=db_keys.study_working,
            name="30 day oral",
            type="St",
            has_multiple_generations=False,
            chemical="2,3,7,8-Tetrachlorodibenzo-P-dioxin",
            cas="1746-01-6",
            chemical_source="ABC Inc.",
            purity_available=True,
            purity_qualifier="≥",
            purity=99.9,
            vehicle="DMSO",
            guideline_compliance="not reported",
            description="Details here.",
        )
        return data

    def test_success(self, db_keys):
        data = self._get_valid_dataset(db_keys)
        serializer = ExperimentSerializer(data=data)
        assert serializer.is_valid()

    def test_dtxsid_validator(self, db_keys):
        data = self._get_valid_dataset(db_keys)

        # should be valid with no dtxsid
        data.pop("dtxsid", None)
        serializer = ExperimentSerializer(data=data)
        assert serializer.is_valid()
        assert "dtxsid" not in serializer.validated_data

        # should be valid with a valid, existing dtxsid
        data["dtxsid"] = DSSTox.objects.first().dtxsid
        serializer = ExperimentSerializer(data=data)
        assert serializer.is_valid()
        assert "dtxsid" in serializer.validated_data

        # should be invalid with an invalid dtxsid
        data["dtxsid"] = "invalid"
        serializer = ExperimentSerializer(data=data)
        assert serializer.is_valid() is False
        assert "dtxsid" not in serializer.validated_data


@pytest.mark.django_db
class TestDosingRegimeSerializer:
    def test_success(self):
        data = {
            "doses": [
                {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 1},
                {"dose_group_id": 1, "dose": 1.0, "dose_units_id": 1},
                {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 2},
                {"dose_group_id": 1, "dose": 10.0, "dose_units_id": 2},
            ],
            "route_of_exposure": "OR",
        }
        serializer = DosingRegimeSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["num_dose_groups"] == 2

    def test_dose_group_failures(self):
        datasets = [
            # `dose_group_id` doesn't start at 0
            {
                "doses": [
                    {"dose_group_id": 1, "dose": 0.0, "dose_units_id": 1},
                    {"dose_group_id": 2, "dose": 1.0, "dose_units_id": 1},
                ],
                "route_of_exposure": "OR",
            },
            # `dose_group_id` doesn't skips 1
            {
                "doses": [
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 1},
                    {"dose_group_id": 2, "dose": 1.0, "dose_units_id": 1},
                ],
                "route_of_exposure": "OR",
            },
            # duplicate dose_group_id/dose_units_id
            {
                "doses": [
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 1},
                    {"dose_group_id": 0, "dose": 1.0, "dose_units_id": 1},
                ],
                "route_of_exposure": "OR",
            },
            # missing dose_group_id/dose_units_id
            {
                "doses": [
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 1},
                    {"dose_group_id": 1, "dose": 1.0, "dose_units_id": 1},
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 2},
                ],
                "route_of_exposure": "OR",
            },
            # missing dose_group_id/dose_units_id pair
            {
                "doses": [
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 1},
                    {"dose_group_id": 1, "dose": 1.0, "dose_units_id": 1},
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 2},
                    {"dose_group_id": 0, "dose": 0.0, "dose_units_id": 2},
                ],
                "route_of_exposure": "OR",
            },
        ]
        for data in datasets:
            serializer = DosingRegimeSerializer(data=data)
            assert serializer.is_valid() is False
