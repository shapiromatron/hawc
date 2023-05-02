import {COLORS, defineAxis, defineFilter, defineProps, defineTable} from "./shared";

// ESD = epi study design
const ESD = {
        studyId: defineProps("studyId", "Study ID", "study-id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study-short_citation"),
    },
    ESDv2Settings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(ESD.studyCitation),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(ESD.studyCitation, {on_click_event: "study"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(ESD.studyCitation, {on_click_event: "study"}),
        },
    };
ESDv2Settings.DASHBOARDS = [
    {
        id: "DEF",
        label: "DEF",
        upperColor: COLORS.blue,
        x_axis: ESDv2Settings.AXIS_OPTIONS.studyCitation.id,
        y_axis: ESDv2Settings.AXIS_OPTIONS.studyCitation.id,
        filters: [ESDv2Settings.FILTER_OPTIONS.studyCitation.id],
        table_fields: [ESDv2Settings.TABLE_FIELDS.studyCitation.id],
    },
];

// ER = epi results
const ER = {
        studyId: defineProps("studyId", "Study ID", "study-id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study-short_citation"),
    },
    ERv2Settings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(ER.studyCitation),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(ER.studyCitation, {on_click_event: "study"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(ER.studyCitation, {on_click_event: "study"}),
        },
        DASHBOARDS: [],
    };
ERv2Settings.DASHBOARDS = [
    {
        id: "ABC",
        label: "ABC",
        upperColor: COLORS.blue,
        x_axis: ESDv2Settings.AXIS_OPTIONS.studyCitation.id,
        y_axis: ESDv2Settings.AXIS_OPTIONS.studyCitation.id,
        filters: [ESDv2Settings.FILTER_OPTIONS.studyCitation.id],
        table_fields: [ESDv2Settings.TABLE_FIELDS.studyCitation.id],
    },
];

export {ERv2Settings, ESDv2Settings};
