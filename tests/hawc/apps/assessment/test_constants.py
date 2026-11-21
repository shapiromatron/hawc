import pytest

from hawc.apps.assessment.constants import (
    AssessmentPermissions,
    AssessmentViewSetPermissions,
    PeerReviewType,
)


class TestPeerReviewType:
    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (PeerReviewType.CONTRACT, True),
            (PeerReviewType.NONE, False),
            (PeerReviewType.OTHER, False),
            (PeerReviewType.NA, False),
        ],
    )
    def test_display(self, status: PeerReviewType, expected):
        assert status.display() is expected
