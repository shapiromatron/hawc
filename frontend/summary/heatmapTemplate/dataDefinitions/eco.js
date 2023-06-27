import {COLORS, defineAxis, defineFilter, defineProps, defineTable} from "./shared";

// EcSD = eco study design
const EcSD = {
        studyId: defineProps("studyId", "Study ID", "study-id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study-short_citation"),
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
    },
    EcRSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(EcR.studyCitation),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(EcR.studyCitation, {on_click_event: "study"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(EcR.studyCitation, {on_click_event: "study"}),
        },
        DASHBOARDS: [],
    };
EcRSettings.DASHBOARDS = [
    {
        id: "ABC",
        label: "ABC",
        upperColor: COLORS.blue,
        x_axis: EcSDSettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: EcSDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [EcSDSettings.FILTER_OPTIONS.studyCitation.id],
        table_fields: [EcSDSettings.TABLE_FIELDS.studyCitation.id],
    },
];

export {EcRSettings, EcSDSettings};
