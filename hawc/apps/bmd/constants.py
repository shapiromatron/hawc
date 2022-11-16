import json
from functools import lru_cache
from pathlib import Path

from django.db import models


class BmdsVersion(models.TextChoices):
    BMDS2601 = "BMDS2601", "BMDS 2.6.0.1"
    BMDS270 = "BMDS270", "BMDS 2.7"
    BMDS330 = "BMDS330", "BMDS 3.3 (2022.10)"


@lru_cache()
def bmds2_logic() -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / "logic.json").read_text())["objects"]
