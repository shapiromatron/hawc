import {
    COLORS,
    defineAxis,
    defineFilter,
    defineMultiAxis,
    defineProps,
    defineTable,
} from "./shared";

// ESD = epi study design
const ESD = {
        studyId: defineProps("studyId", "Study ID", "study id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study citation"),
        studyIdentifier: defineProps("studyIdentifier", "Study identifier", "study identifier"),
        studyEval: defineProps("studyEval", "Overall study evaluation", "overall study evaluation"),
        studyDesign: defineProps("studyDesign", "Study design", "study design"),
        studyPopulationSource: defineProps(
            "studyPopulationSource",
            "Study population source",
            "study population source"
        ),
        exposureName: defineProps("exposureName", "Exposure name", "exposure name"),
        exposureRoute: defineProps("exposureRoute", "Exposure route", "exposure route"),
        exposureMeasure: defineProps("exposureMeasure", "Exposure measure", "exposure measure"),
        exposureMetric: defineProps("exposureMetric", "Exposure metric", "exposure metric"),
        system: defineProps("system", "System", "system"),
        effect: defineProps("effect", "Effect", "effect"),
        effectSubtype: defineProps("effectSubtype", "Effect subtype", "effect subtype"),
    },
    ESDSettings = {
        AXIS_OPTIONS: {
            exposureName: defineAxis(ESD.exposureName, {delimiter: "|"}),
            exposureRoute: defineAxis(ESD.exposureRoute, {delimiter: "|"}),
            exposureMeasure: defineAxis(ESD.exposureMeasure, {delimiter: "|"}),
            exposureMetric: defineAxis(ESD.exposureMetric, {delimiter: "|"}),
            exposureMeasureMetric: defineMultiAxis(
                [ESD.exposureMeasure, ESD.exposureMetric],
                "exposureMeasureMetric",
                "Exposure measurement & metric",
                {delimiter: "|"}
            ),
            studyCitation: defineAxis(ESD.studyCitation),
            studyEval: defineAxis(ESD.studyEval, {delimiter: "|"}),
            studyDesign: defineAxis(ESD.studyDesign, {delimiter: "|"}),
            studyPopulationSource: defineAxis(ESD.studyPopulationSource, {delimiter: "|"}),
            system: defineAxis(ESD.system, {delimiter: "|"}),
            effect: defineAxis(ESD.effect, {delimiter: "|"}),
            systemEffect: defineMultiAxis(
                [ESD.system, ESD.effect],
                "systemEffect",
                "System & Effect",
                {delimiter: "|"}
            ),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(ESD.studyCitation, {on_click_event: "study"}),
            studyEval: defineFilter(ESD.studyEval),
            studyDesign: defineFilter(ESD.studyDesign, {delimiter: "|"}),
            studyPopulationSource: defineFilter(ESD.studyPopulationSource, {delimiter: "|"}),
            exposureMeasure: defineFilter(ESD.exposureMeasure, {delimiter: "|"}),
            exposureMetric: defineFilter(ESD.exposureMetric, {delimiter: "|"}),
            exposureRoute: defineFilter(ESD.exposureRoute, {delimiter: "|"}),
            system: defineFilter(ESD.system, {delimiter: "|"}),
            effect: defineFilter(ESD.effect, {delimiter: "|"}),
            effectSubtype: defineFilter(ESD.effectSubtype, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(ESD.studyCitation, {on_click_event: "study"}),
            studyIdentifier: defineTable(ESD.studyIdentifier, {on_click_event: "study"}),
            studyEval: defineTable(ESD.studyEval),
            studyDesign: defineTable(ESD.studyDesign, {delimiter: "|"}),
            studyPopulationSource: defineTable(ESD.studyPopulationSource, {delimiter: "|"}),
            exposureName: defineTable(ESD.exposureName, {delimiter: "|"}),
            exposureRoute: defineTable(ESD.exposureRoute, {delimiter: "|"}),
            exposureMeasure: defineTable(ESD.exposureMeasure, {delimiter: "|"}),
            exposureMetric: defineTable(ESD.exposureMetric, {delimiter: "|"}),
            system: defineTable(ESD.system, {delimiter: "|"}),
            effect: defineTable(ESD.effect, {delimiter: "|"}),
            effectSubtype: defineTable(ESD.effectSubtype, {delimiter: "|"}),
        },
    };
ESDSettings.DASHBOARDS = [
    {
        id: "study design vs. system & effect",
        label: "study design vs. system & effect",
        upperColor: COLORS.blue,
        x_axis: ESDSettings.AXIS_OPTIONS.studyDesign.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.studyDesign.id,
            ESDSettings.TABLE_FIELDS.studyPopulationSource.id,
            ESDSettings.TABLE_FIELDS.exposureRoute.id,
            ESDSettings.TABLE_FIELDS.exposureMeasure.id,
            ESDSettings.TABLE_FIELDS.exposureMetric.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "exposure measure vs. system & effect",
        label: "exposure measure vs. system & effect",
        upperColor: COLORS.red,
        x_axis: ESDSettings.AXIS_OPTIONS.exposureMeasure.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.studyDesign.id,
            ESDSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.studyDesign.id,
            ESDSettings.TABLE_FIELDS.studyPopulationSource.id,
            ESDSettings.TABLE_FIELDS.exposureRoute.id,
            ESDSettings.TABLE_FIELDS.exposureMeasure.id,
            ESDSettings.TABLE_FIELDS.exposureMetric.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "exposure route vs. system & effect",
        label: "exposure route vs. system & effect",
        upperColor: COLORS.purple,
        x_axis: ESDSettings.AXIS_OPTIONS.exposureRoute.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.studyDesign.id,
            ESDSettings.FILTER_OPTIONS.exposureMetric.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.studyDesign.id,
            ESDSettings.TABLE_FIELDS.studyPopulationSource.id,
            ESDSettings.TABLE_FIELDS.exposureRoute.id,
            ESDSettings.TABLE_FIELDS.exposureMeasure.id,
            ESDSettings.TABLE_FIELDS.exposureMetric.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-study-pop-source-vs-system-effect",
        label: "study population source vs. system & effect",
        upperColor: COLORS.orange,
        x_axis: ESDSettings.AXIS_OPTIONS.studyPopulationSource.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.studyDesign.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.studyDesign.id,
            ESDSettings.TABLE_FIELDS.studyPopulationSource.id,
            ESDSettings.TABLE_FIELDS.exposureRoute.id,
            ESDSettings.TABLE_FIELDS.exposureMeasure.id,
            ESDSettings.TABLE_FIELDS.exposureMetric.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "system vs. citation",
        label: "system vs. citation",
        upperColor: COLORS.green,
        x_axis: ESDSettings.AXIS_OPTIONS.system.id,
        y_axis: ESDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyDesign.id,
            ESDSettings.FILTER_OPTIONS.studyPopulationSource.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
            ESDSettings.FILTER_OPTIONS.effect.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.studyDesign.id,
            ESDSettings.TABLE_FIELDS.studyPopulationSource.id,
            ESDSettings.TABLE_FIELDS.exposureRoute.id,
            ESDSettings.TABLE_FIELDS.exposureMeasure.id,
            ESDSettings.TABLE_FIELDS.exposureMetric.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "system & effect vs. citation",
        label: "system & effect vs. citation",
        upperColor: COLORS.red,
        x_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        y_axis: ESDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyDesign.id,
            ESDSettings.FILTER_OPTIONS.studyPopulationSource.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
            ESDSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.studyDesign.id,
            ESDSettings.TABLE_FIELDS.studyPopulationSource.id,
            ESDSettings.TABLE_FIELDS.exposureRoute.id,
            ESDSettings.TABLE_FIELDS.exposureMeasure.id,
            ESDSettings.TABLE_FIELDS.exposureMetric.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
];

// ER = epi results
const ER = {
        studyId: defineProps("studyId", "Study ID", "study id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study citation"),
        studyIdentifier: defineProps("studyIdentifier", "Study identifier", "study identifier"),
        studyEval: defineProps("studyEval", "Overall study evaluation", "overall study evaluation"),
        studyPopulationId: defineProps(
            "studyPopulationId",
            "Study Population ID",
            "study population id"
        ),
        studyPopulationName: defineProps(
            "studyPopulationName",
            "Study population name",
            "study population name"
        ),
        studyPopulationSource: defineProps(
            "studyPopulationSource",
            "Study population source",
            "study population source"
        ),
        studyDesign: defineProps("studyDesign", "Study design", "study design"),
        comparisonSetId: defineProps("comparisonSetId", "comparison set ID", "comparison set id"),
        comparisonSetName: defineProps(
            "comparisonSetName",
            "Comparison set name",
            "comparison set name"
        ),
        exposureId: defineProps("exposureId", "Exposure ID", "exposure id"),
        exposureName: defineProps("exposureName", "Exposure name", "exposure name"),
        exposureRoute: defineProps("exposureRoute", "Exposure route", "exposure route"),
        exposureMeasure: defineProps("exposureMeasure", "Exposure measure", "exposure measure"),
        exposureMetric: defineProps("exposureMetric", "Exposure metric", "exposure metric"),
        outcomeId: defineProps("outcomeId", "Outcome ID", "outcome id"),
        outcomeName: defineProps("outcomeName", "Outcome name", "outcome name"),
        system: defineProps("system", "System", "system"),
        effect: defineProps("effect", "Effect", "effect"),
        effectSubtype: defineProps("effectSubtype", "Effect subtype", "effect subtype"),
        resultId: defineProps("resultId", "Result ID", "result id"),
        resultName: defineProps("resultName", "Result name", "result name"),
    },
    ERSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(ER.studyCitation),
            studyEval: defineAxis(ER.studyEval),
            studyPopulationSource: defineAxis(ER.studyPopulationSource),
            studyDesign: defineAxis(ER.studyDesign),
            exposureName: defineAxis(ER.exposureName),
            exposureRoute: defineAxis(ER.exposureRoute, {delimiter: "|"}),
            exposureMeasureMetric: defineMultiAxis(
                [ER.exposureMeasure, ER.exposureMetric],
                "exposureMeasureMetric",
                "Exposure Measure & Metric"
            ),
            exposureMeasure: defineAxis(ER.exposureMeasure),
            exposureMetric: defineAxis(ER.exposureMetric),
            systemEffect: defineMultiAxis(
                [ER.system, ER.effect],
                "systemEffect",
                "System & Effect"
            ),
            system: defineAxis(ER.system),
            effect: defineAxis(ER.effect),
            effectSubtype: defineAxis(ER.effectSubtype),
            resultName: defineAxis(ER.resultName),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(ER.studyCitation, {on_click_event: "study"}),
            studyEval: defineFilter(ER.studyEval),
            studyDesign: defineFilter(ER.studyDesign),
            studyPopulationSource: defineFilter(ER.studyPopulationSource),
            exposureRoute: defineFilter(ER.exposureRoute, {delimiter: "|"}),
            exposureMeasure: defineFilter(ER.exposureMeasure),
            exposureMetric: defineFilter(ER.exposureMetric),
            system: defineFilter(ER.system),
            effect: defineFilter(ER.effect),
            effectSubtype: defineFilter(ER.effectSubtype),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(ER.studyCitation, {on_click_event: "study"}),
            studyEval: defineTable(ER.studyEval),
            studyPopulationName: defineTable(ER.studyPopulationName, {
                on_click_event: "study_population",
            }),
            studyPopulationSource: defineTable(ER.studyPopulationSource),
            studyDesign: defineTable(ER.studyDesign),
            comparisonSetName: defineTable(ER.comparisonSetName, {
                on_click_event: "comparison_set",
            }),
            exposureName: defineTable(ER.exposureName, {on_click_event: "exposure"}),
            exposureRoute: defineTable(ER.exposureRoute, {delimiter: "|"}),
            exposureMeasure: defineTable(ER.exposureMeasure),
            exposureMetric: defineTable(ER.exposureMetric),
            outcomeName: defineTable(ER.outcomeName, {on_click_event: "outcome"}),
            system: defineTable(ER.system),
            effect: defineTable(ER.effect),
            effectSubtype: defineTable(ER.effectSubtype),
            resultName: defineTable(ER.resultName, {on_click_event: "result"}),
        },
        DASHBOARDS: [],
    };
ERSettings.DASHBOARDS = [
    {
        id: "study design vs. system & effect",
        label: "study design vs. system & effect",
        upperColor: COLORS.blue,
        x_axis: ERSettings.AXIS_OPTIONS.studyDesign.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.studyPopulationSource.id,
            ERSettings.FILTER_OPTIONS.exposureMeasure.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.studyPopulationName.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.system.id,
            ERSettings.TABLE_FIELDS.effect.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "exposure measure & metric vs. system & effect",
        label: "exposure measure & metric vs. system & effect",
        upperColor: COLORS.orange,
        x_axis: ERSettings.AXIS_OPTIONS.exposureMeasureMetric.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.studyDesign.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.studyPopulationName.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.system.id,
            ERSettings.TABLE_FIELDS.effect.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "exposure route vs. system & effect",
        label: "exposure route vs. system & effect",
        upperColor: COLORS.green,
        x_axis: ERSettings.AXIS_OPTIONS.exposureRoute.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.studyDesign.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
            ERSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.studyPopulationName.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.system.id,
            ERSettings.TABLE_FIELDS.effect.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "study population source vs. system & effect",
        label: "study population source vs. system & effect",
        upperColor: COLORS.red,
        x_axis: ERSettings.AXIS_OPTIONS.studyPopulationSource.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.studyDesign.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
            ERSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.studyPopulationName.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.system.id,
            ERSettings.TABLE_FIELDS.effect.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "system vs. citation",
        label: "system vs. citation",
        upperColor: COLORS.purple,
        x_axis: ERSettings.AXIS_OPTIONS.system.id,
        y_axis: ERSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.effect.id,
            ERSettings.FILTER_OPTIONS.exposureMeasure.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.studyPopulationName.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.system.id,
            ERSettings.TABLE_FIELDS.effect.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "effect vs. citation",
        label: "effect vs. citation",
        upperColor: COLORS.black,
        x_axis: ERSettings.AXIS_OPTIONS.effect.id,
        y_axis: ERSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.studyDesign.id,
            ERSettings.FILTER_OPTIONS.exposureMeasure.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.studyPopulationName.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.system.id,
            ERSettings.TABLE_FIELDS.effect.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
];

export {ERSettings, ESDSettings};
