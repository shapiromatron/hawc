from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from ...assessment.models import Assessment


def get_published_only(assessment: Assessment, request: Request) -> bool:
    """Get published content only.

    Returns true if a user cannot edit this assessment OR if a user can edit
    but they did not request the unpublished data.

    Args:
        assessment (Assessment): selected assessment
        request (Request): a DRF request instance
    """
    unpublished_requested = request.query_params.get("unpublished", "").lower() == "true"
    can_edit = assessment.user_is_team_member_or_higher(request.user)
    if unpublished_requested and not can_edit:
        raise PermissionDenied("You must be part of the team to view unpublished data")
    return not (can_edit and unpublished_requested)
