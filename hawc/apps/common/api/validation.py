from typing import TypeVar

from django.db.models import Choices
from rest_framework.exceptions import ValidationError

T = TypeVar("T", bound=Choices)


def get_enum_or_400(value, Choice: type[T]) -> T:
    try:
        return Choice(value)
    except ValueError:
        raise ValidationError([f"Invalid choice {value}"]) from None
