import pytest

from hawc.apps.animal.serializers import DosingRegimeSerializer


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
