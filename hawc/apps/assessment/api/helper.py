from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.request import Request

from ...common.helper import tryParseInt
from .. import models


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Please provide an `assessment_id` argument to your GET request."


class InvalidAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Assessment does not exist for given `assessment_id`."


def get_assessment_id_param(request: Request) -> int:
    """
    If request doesn't contain an integer-based `assessment_id`, an exception is raised.
    """
    assessment_id = tryParseInt(
        request.query_params.get("assessment_id") or request.data.get("assessment_id")
    )
    if assessment_id is None:
        raise RequiresAssessmentID()
    return assessment_id


def get_assessment_from_query(request: Request) -> models.Assessment | None:
    """Returns assessment or raises exception if does not exist."""
    assessment_id = get_assessment_id_param(request)
    try:
        return models.Assessment.objects.get(pk=assessment_id)
    except models.Assessment.DoesNotExist:
        raise InvalidAssessmentID()
