import pytest
from django.db.models import Q

from hawc.apps.mgmt.constants import TaskStatus


class TestTaskStatus:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (990, [10, 20]),
            (995, [30, 40]),
            (20, 20),
        ],
    )
    def test_filters(self, value, expected):
        filters = {"status__in": expected} if isinstance(expected, list) else {"status": expected}
        assert TaskStatus.filter_extra(value) == Q(**filters)

    def test_extra_choices(self):
        assert TaskStatus.extra_choices() == [
            (990, "Active"),
            (995, "Inactive"),
            *TaskStatus.choices,
        ]
