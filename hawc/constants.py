import json
import os
from enum import Enum

from pydantic import BaseModel


class AuthProvider(str, Enum):
    django = "django"
    external = "external"


class FeatureFlags(BaseModel):
    THIS_IS_AN_EXAMPLE: bool = True
    ENABLE_ECO: bool = False
    FIPS: bool = False

    @classmethod
    def from_env(cls, variable) -> "FeatureFlags":
        return cls.parse_obj(json.loads(os.environ.get(variable, "{}")))
