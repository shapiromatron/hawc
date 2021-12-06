from enum import IntEnum
from typing import Dict

NO_LABEL = "---"


class IntChoiceEnum(IntEnum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def as_dict(cls) -> Dict:
        return {key.value: key.name for key in cls}
