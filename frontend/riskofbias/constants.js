let NA_KEY = 1,
    NR_KEY = 2,
    SCORE_TEXT = {
        1: 'N/A',
        2: 'NR',

        14: '--',
        15: '-',
        16: '+',
        17: '++',

        24: '--',
        25: '-',
        26: '+',
        27: '++',
    },
    SCORE_SHADES = {
        1: '#FFCC00',
        2: '#FFCC00',

        14: '#CC3333',
        15: '#FFCC00',
        16: '#6FFF00',
        17: '#00CC00',

        24: '#CC3333',
        25: '#FFCC00',
        26: '#6FFF00',
        27: '#00CC00',
    },
    SCORE_BAR_WIDTH_PERCENTAGE = {
        1: 50,
        2: 50,

        14: 25,
        15: 50,
        16: 75,
        17: 100,

        24: 25,
        25: 50,
        26: 75,
        27: 100,
    },
    SCORE_TEXT_DESCRIPTION = {
        1: 'Not applicable',
        2: 'Not reported',

        14: 'Definitely high risk of bias',
        15: 'Probably high risk of bias',
        16: 'Probably low risk of bias',
        17: 'Definitely low risk of bias',

        24: 'Critically deficient',
        25: 'Deficient',
        26: 'Adequate',
        27: 'Good',
    },
    COLLAPSED_NR_FIELDS_DESCRIPTION = {
        15: 'Probably high risk of bias/not reported',
        25: 'Deficient/not reported',
    };

export {
    NA_KEY,
    NR_KEY,
    SCORE_TEXT,
    SCORE_SHADES,
    SCORE_TEXT_DESCRIPTION,
    SCORE_BAR_WIDTH_PERCENTAGE,
    COLLAPSED_NR_FIELDS_DESCRIPTION,
};
