from typing import Dict, List, Tuple

from django.db import models


class RiskOfBiasResponses(models.IntegerChoices):
    NONE = 0, "None"
    HIGH_LOW_BIAS = 1, "High/Low risk of bias"
    GOOD_DEFICIENT = 2, "Good/deficient"
    HIGH_LOW_CONFIDENCE = 3, "High/low confidence"
    YES_NO = 4, "Yes/No"
    MINOR_CRITICAL = 5, "Minor/Critical concerns"


RESPONSES_VALUES: Dict[models.IntegerChoices, List[int]] = {
    RiskOfBiasResponses.NONE: [0],
    RiskOfBiasResponses.HIGH_LOW_BIAS: [17, 16, 15, 12, 14, 10],
    RiskOfBiasResponses.GOOD_DEFICIENT: [27, 26, 25, 24, 22, 20],
    RiskOfBiasResponses.HIGH_LOW_CONFIDENCE: [37, 36, 35, 34, 22, 20],
    RiskOfBiasResponses.YES_NO: [40, 41, 22, 20],
    RiskOfBiasResponses.MINOR_CRITICAL: [51, 50, 22, 20],
}

RESPONSES_VALUES_DEFAULT: Dict[models.IntegerChoices, int] = {
    RiskOfBiasResponses.NONE: 0,
    RiskOfBiasResponses.HIGH_LOW_BIAS: 12,
    RiskOfBiasResponses.GOOD_DEFICIENT: 22,
    RiskOfBiasResponses.HIGH_LOW_CONFIDENCE: 22,
    RiskOfBiasResponses.YES_NO: 22,
    RiskOfBiasResponses.MINOR_CRITICAL: 22,
}


SCORE_CHOICES: Tuple[Tuple[int, str], ...] = (
    (0, "None"),
    (10, "Not applicable"),
    (12, "Not reported"),
    (14, "Definitely high risk of bias"),
    (15, "Probably high risk of bias"),
    (16, "Probably low risk of bias"),
    (17, "Definitely low risk of bias"),
    (20, "Not applicable"),
    (22, "Not reported"),
    (24, "Critically deficient"),
    (25, "Deficient"),
    (26, "Adequate"),
    (27, "Good"),
    (34, "Uninformative"),
    (35, "Low confidence"),
    (36, "Medium confidence"),
    (37, "High confidence"),
    (40, "Yes"),
    (41, "No"),
    (50, "Critical concerns"),
    (51, "No/minor concerns"),
)

SCORE_CHOICES_MAP: Dict[int, str] = {k: v for k, v in SCORE_CHOICES}

NA_SCORES: Tuple[int, ...] = (10, 20)

SCORE_SYMBOLS: Dict[int, str] = {
    0: "━",
    10: "N/A",
    12: "NR",
    14: "--",
    15: "-",
    16: "+",
    17: "++",
    20: "N/A",
    22: "NR",
    24: "--",
    25: "-",
    26: "+",
    27: "++",
    34: "--",
    35: "-",
    36: "+",
    37: "++",
    40: "Y",
    41: "N",
    50: "-",
    51: "+",
}

SCORE_SHADES: Dict[int, str] = {
    0: "#DFDFDF",
    10: "#E8E8E8",
    12: "#FFCC00",
    14: "#CC3333",
    15: "#FFCC00",
    16: "#6FFF00",
    17: "#00CC00",
    20: "#E8E8E8",
    22: "#FFCC00",
    24: "#CC3333",
    25: "#FFCC00",
    26: "#6FFF00",
    27: "#00CC00",
    34: "#CC3333",
    35: "#FFCC00",
    36: "#6FFF00",
    37: "#00CC00",
    40: "#00CC00",
    41: "#CC3333",
    50: "#CC3333",
    51: "#6FFF00",
}


class BiasDirections(models.IntegerChoices):
    BIAS_DIRECTION_UNKNOWN = 0, "not entered/unknown"
    BIAS_DIRECTION_UP = 1, "⬆ (away from null)"
    BIAS_DIRECTION_DOWN = 2, "⬇ (towards null)"
