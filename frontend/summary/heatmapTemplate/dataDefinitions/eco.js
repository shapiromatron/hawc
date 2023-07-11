import {COLORS, defineAxis, defineFilter, defineMultiAxis, defineProps, defineTable} from "./shared";

// EcSD = eco study design
const EcSD = {
        studyId: defineProps("studyId", "Study ID", "study-id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study-short_citation"),
        designValue: defineProps("designValue", "Design Value", "design-design__value"),
        designClimates: defineProps("designClimates", "Design Climates", "design-climates_"),
        designCountries: defineProps("designCountries", "Design Countries", "design-countries"),
        designStates: defineProps("designStates", "Design States", "design-states"),
        causeTerm: defineProps("causeTerm", "Cause Term", "cause-term"),
        effectTerm: defineProps("effectTerm", "EFfect Term", "effect-term"),
        resultName: defineProps("resultName", "Result Name", "result-name"),
    },
    EcSDSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(EcSD.studyCitation),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(EcSD.studyCitation, {on_click_event: "study"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(EcSD.studyCitation, {on_click_event: "study"}),
        },
    };
EcSDSettings.DASHBOARDS = [
    {
        id: "DEF",
        label: "DEF",
        upperColor: COLORS.blue,
        x_axis: EcSDSettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: EcSDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [EcSDSettings.FILTER_OPTIONS.studyCitation.id],
        table_fields: [EcSDSettings.TABLE_FIELDS.studyCitation.id],
    },
];

// EcR = eco results
const EcR = {
        studyId: defineProps("studyId", "Study ID", "study-id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study-short_citation"),
        designValue: defineProps("designValue", "Design Value", "design-design__value"),
        designName: defineProps("designName", "Design Name", "design-name"),
        designClimates: defineProps("designClimates", "Design Climates", "design-climates_"),
        designEcoregions: defineProps("designEcoregions", "Design Ecoregions", "design-ecoregions"),
        designCountries: defineProps("designCountries", "Design Countries", "design-countries"),
        designStates: defineProps("designStates", "Design States", "design-states"),
        causeName: defineProps("causeName", "Cause Name", "cause-name"),
        effectName: defineProps("effectName", "Effect Name", "effect-name"),
        resultName: defineProps("resultName", "Result Name", "result-name"),
    },
    EcRSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(EcR.studyCitation),
            causeName: defineAxis(EcR.causeName),
            effectName: defineAxis(EcR.effectName),
            causeEffect: defineMultiAxis([EcR.causeName, EcR.effectName], "causeEffect", "Cause & Effect"),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(EcR.studyCitation, {on_click_event: "study"}),
            designClimates: defineFilter(EcR.designClimates, {delimiter: "|"}),
            designCountries: defineFilter(EcR.designCountries, {delimiter: "|"}),
            designStates: defineFilter(EcR.designStates, {delimiter: "|"}),
            causeName: defineFilter(EcR.causeName, {delimiter: "|"}),
            effectName: defineFilter(EcR.effectName, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(EcR.studyCitation, {on_click_event: "study"}),
            designName: defineTable(EcR.designName),
            designClimates: defineTable(EcR.designName),
            designEcoregions: defineTable(EcR.designEcoregions),
            resultName: defineTable(EcR.resultName, {delimiter: "|"}),
            effectName: defineTable(EcR.effectName),
            causeName: defineTable(EcR.causeName),
        },
        DASHBOARDS: [],
    };
EcRSettings.DASHBOARDS = [
    {
        id: "effect vs. reference",
        label: "effect vs. reference",
        upperColor: COLORS.blue,
        x_axis: EcRSettings.AXIS_OPTIONS.effectName.id,
        y_axis: EcRSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            EcRSettings.FILTER_OPTIONS.designClimates.id,
            EcRSettings.FILTER_OPTIONS.designCountries.id,
            EcRSettings.FILTER_OPTIONS.designStates.id,
        ],
        table_fields: [
            EcRSettings.TABLE_FIELDS.studyCitation.id,
            EcRSettings.TABLE_FIELDS.designName.id,
            EcRSettings.TABLE_FIELDS.designClimates.id,
            EcRSettings.TABLE_FIELDS.designEcoregions.id,
        ]
    },
    {
        id: "cause & effect vs. reference",
        label: "cause & effect vs. reference",
        upperColor: COLORS.blue,
        x_axis: EcRSettings.AXIS_OPTIONS.causeEffect.id,
        y_axis: EcRSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            EcRSettings.FILTER_OPTIONS.designClimates.id,
            EcRSettings.FILTER_OPTIONS.designCountries.id,
            EcRSettings.FILTER_OPTIONS.designStates.id,
        ],
        table_fields: [
            EcRSettings.TABLE_FIELDS.studyCitation.id,
            EcRSettings.TABLE_FIELDS.designName.id,
            EcRSettings.TABLE_FIELDS.designClimates.id,
            EcRSettings.TABLE_FIELDS.designEcoregions.id,
        ]
    },
    {
        id: "effect vs cause",
        label: "effect vs cause",
        upperColor: COLORS.blue,
        x_axis: EcRSettings.AXIS_OPTIONS.effectName.id,
        y_axis: EcRSettings.AXIS_OPTIONS.causeName.id,
        filters: [
            EcRSettings.FILTER_OPTIONS.studyCitation.id,
            EcRSettings.FILTER_OPTIONS.designCountries.id,
            EcRSettings.FILTER_OPTIONS.designStates.id,
        ],
        table_fields: [
            EcRSettings.TABLE_FIELDS.studyCitation.id,
            EcRSettings.TABLE_FIELDS.designName.id,
            EcRSettings.TABLE_FIELDS.designClimates.id,
            EcRSettings.TABLE_FIELDS.designEcoregions.id,
        ],
    },
];

export {EcRSettings, EcSDSettings};
