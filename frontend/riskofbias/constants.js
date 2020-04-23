import _ from "lodash";

const NA_KEYS = [10, 20],
    NR_KEYS = [12, 22],
    SCORE_TEXT = {
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
    },
    SCORE_SHADES = {
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
    },
    SCORE_BAR_WIDTH_PERCENTAGE = {
        10: 50,
        12: 50,
        14: 25,
        15: 50,
        16: 75,
        17: 100,

        20: 50,
        22: 50,
        24: 25,
        25: 50,
        26: 75,
        27: 100,
    },
    SCORE_TEXT_DESCRIPTION = {
        10: "Not applicable",
        12: "Not reported",
        14: "Definitely high risk of bias",
        15: "Probably high risk of bias",
        16: "Probably low risk of bias",
        17: "Definitely low risk of bias",

        20: "Not applicable",
        22: "Not reported",
        24: "Critically deficient",
        25: "Deficient",
        26: "Adequate",
        27: "Good",
    },
    SCORE_TEXT_DESCRIPTION_LEGEND = {
        10: "Not applicable",
        12: "Not reported",
        14: "Definitely high risk of bias",
        15: "Probably high risk of bias",
        16: "Probably low risk of bias",
        17: "Definitely low risk of bias",

        20: "Not applicable",
        22: "Not reported",
        24: "Critically deficient (metric) or Uninformative (overall)",
        25: "Deficient (metric) or Low confidence (overall)",
        26: "Adequate (metric) or Medium confidence (overall)",
        27: "Good (metric) or High confidence (overall)",
    },
    BIAS_DIRECTION_UNKNOWN = 0,
    BIAS_DIRECTION_UP = 1,
    BIAS_DIRECTION_DOWN = 2,
    BIAS_DIRECTION_CHOICES = {
        [BIAS_DIRECTION_UNKNOWN]: "? (Unknown/not specified)",
        [BIAS_DIRECTION_UP]: "⬆ (Away from null)",
        [BIAS_DIRECTION_DOWN]: "⬇ (Towards null)",
    },
    BIAS_DIRECTION_COMPACT = {
        [BIAS_DIRECTION_UNKNOWN]: "",
        [BIAS_DIRECTION_UP]: "▲",
        [BIAS_DIRECTION_DOWN]: "▼",
    },
    BIAS_DIRECTION_SIMPLE = {
        [BIAS_DIRECTION_UNKNOWN]: "",
        [BIAS_DIRECTION_UP]: "⬆",
        [BIAS_DIRECTION_DOWN]: "⬇",
    },
    BIAS_DIRECTION_VERBOSE = {
        [BIAS_DIRECTION_UNKNOWN]: "",
        [BIAS_DIRECTION_UP]: "Bias direction up (Away from null)",
        [BIAS_DIRECTION_DOWN]: "Bias direction down (Towards null)",
    },
    COLLAPSED_NR_FIELDS_DESCRIPTION = {
        15: "Probably high risk of bias/not reported",
        25: "Deficient/not reported",
    },
    getMultiScoreDisplaySettings = function(scores) {
        // Return visualization/color settings for situations where multiple scores may exist for
        // a given metric (eg, study-level override settings)
        let sortedScores = _.orderBy(scores, "score", "desc"),
            defaultScore = _.find(scores, {is_default: true}),
            shades = _.chain(sortedScores)
                .map(score => score.score_shade)
                .uniq()
                .value(),
            symbols = _.chain(sortedScores)
                .map(score => score.score_symbol)
                .uniq()
                .value(),
            symbolText = symbols.join(" / "),
            symbolShortText = symbols.length === 1 ? symbols[0] : `${defaultScore.score_symbol}*`,
            directions = _.chain(sortedScores)
                .map(score => score.bias_direction)
                .uniq()
                .value(),
            directionText = _.chain(directions)
                .map(d => BIAS_DIRECTION_SIMPLE[d])
                .value()
                .join(""),
            reactStyle,
            svgStyle,
            cssStyle;

        if (shades.length == 1) {
            reactStyle = {backgroundColor: shades[0]};
            cssStyle = {"background-color": shades[0]};
            svgStyle = {fill: shades[0]};
        } else if (shades.length >= 2) {
            let dim = Math.ceil(50 / shades.length),
                reactGradients = shades
                    .map((shade, idx) => `${shade} ${idx * dim}px, ${shade} ${(idx + 1) * dim}px`)
                    .join(", "),
                svgShades = shades
                    .map((shade, idx) => {
                        const offset1 = Math.ceil((idx / shades.length) * 100),
                            offset2 = Math.ceil(((idx + 1) / shades.length) * 100);
                        return `<stop offset="${offset1}%" stop-color="${shade}" stop-opacity="1" />
                                <stop offset="${offset2}%" stop-color="${shade}" stop-opacity="1" />`;
                    })
                    .join(""),
                gradientId = `gradient${scores[0].id}`,
                gradient = `<linearGradient id="${gradientId}" x1="0" y1="0" x2="5%" y2="5%" spreadMethod="repeat">${svgShades}</linearGradient>`;

            reactStyle = {background: `repeating-linear-gradient(-45deg, ${reactGradients})`};
            cssStyle = reactStyle;
            svgStyle = {
                gradient,
                fill: `url(#${gradientId})`,
            };
        }

        return {
            reactStyle,
            cssStyle,
            symbolText,
            symbolShortText,
            directions,
            directionText,
            svgStyle,
        };
    },
    OVERRIDE_SCORE_LABEL_MAPPING = {
        "animal.endpoint": "Animal bioassay endpoints",
        "animal.animalgroup": "Animal bioassay groups",
        "epi.outcome": "Epidemiological outcomes",
        "epi.exposure": "Epidemiological exposures",
        "epi.result": "Epidemiological results",
    };

export {
    NA_KEYS,
    NR_KEYS,
    SCORE_TEXT,
    SCORE_SHADES,
    SCORE_TEXT_DESCRIPTION,
    SCORE_TEXT_DESCRIPTION_LEGEND,
    BIAS_DIRECTION_UNKNOWN,
    BIAS_DIRECTION_UP,
    BIAS_DIRECTION_DOWN,
    BIAS_DIRECTION_CHOICES,
    BIAS_DIRECTION_SIMPLE,
    BIAS_DIRECTION_VERBOSE,
    BIAS_DIRECTION_COMPACT,
    SCORE_BAR_WIDTH_PERCENTAGE,
    COLLAPSED_NR_FIELDS_DESCRIPTION,
    getMultiScoreDisplaySettings,
    OVERRIDE_SCORE_LABEL_MAPPING,
};
