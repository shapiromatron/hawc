import pytest
from model_bakery import baker

from hawc.apps.assessment.constants import AssessmentViewSetPermissions, PeerReviewType
from hawc.apps.assessment.permissions import AssessmentPermissions


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


class TestAssessmentViewSetPermissions:
    @pytest.mark.parametrize(
        ("permission", "user_id", "expected"),
        [
            (AssessmentViewSetPermissions.CAN_VIEW_OBJECT, 3, True),
            (AssessmentViewSetPermissions.CAN_VIEW_OBJECT, 999, False),
            (AssessmentViewSetPermissions.CAN_EDIT_OBJECT, 2, True),
            (AssessmentViewSetPermissions.CAN_EDIT_OBJECT, 3, False),
            (AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER, 2, True),
            (AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER, 999, False),
            (AssessmentViewSetPermissions.PROJECT_MANAGER_OR_HIGHER, 1, True),
            (AssessmentViewSetPermissions.PROJECT_MANAGER_OR_HIGHER, 999, False),
        ],
    )
    def test_has_permission(self, monkeypatch, permission, user_id, expected):
        perms = AssessmentPermissions(
            public=False,
            editable=True,
            project_manager={1},
            team_members={2},
            reviewers={3},
        )
        monkeypatch.setattr(AssessmentPermissions, "get", classmethod(lambda cls, a: perms))
        assessment = baker.prepare("assessment.Assessment", id=1)
        user = baker.prepare("myuser.HAWCUser", id=user_id, is_superuser=False)
        assert permission.has_permission(assessment, user) is expected
