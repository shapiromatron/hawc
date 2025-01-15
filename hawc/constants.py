import json
import os
from enum import Enum

from pydantic import BaseModel


class AuthProvider(str, Enum):
    django = "django"
    external = "external"


class FeatureFlags(BaseModel):
    THIS_IS_AN_EXAMPLE: bool = True
    DEFAULT_LITERATURE_CONFLICT_RESOLUTION: bool = False
    ALLOW_RIS_IMPORTS: bool = True
    FAKE_IMPORTS: bool = False
    ANONYMOUS_ACCOUNT_CREATION: bool = True
    ENABLE_WIP_VISUALS: bool = False
    ENABLE_FILTER_DOWNLOADS: bool = False
    ENABLE_DOCS_LINK: bool = False
    ENABLE_NEW_HERO: bool = False

    @classmethod
    def from_env(cls, variable) -> "FeatureFlags":
        return cls.model_validate(json.loads(os.environ.get(variable, "{}")))


class ColorblindColors:
    """
    A collection of colorblind friendly color pallettes for use in HAWC, as needed.
    Originally gathered from: https://personal.sron.nl/~pault/
    """

    # fmt: off
    BRIGHT = ["#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377", "#BBBBBB"]
    VIBRANT = ["#EE7733", "#0077BB", "#33BBEE", "#EE3377", "#CC3311", "#009988", "#BBBBBB"]
    MUTED = [
        "#CC6677", "#332288", "#DDCC77", "#117733", "#88CCEE",
        "#882255", "#44AA99", "#999933", "#DDDDDD"
    ]
    # fmt: on
