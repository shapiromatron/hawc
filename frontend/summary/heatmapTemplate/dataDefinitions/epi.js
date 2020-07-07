import {defineProps, defineAxis, defineMultiAxis, defineFilter, defineTable} from "./shared";

// ESD = epi study design
const ESD = {
        studyId: defineProps("studyId", "Study ID", "study id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study citation"),
        studyIdentifier: defineProps("studyIdentifier", "Study identifier", "study identifier"),
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
            studyDesign: defineFilter(ESD.studyDesign, {delimiter: "|"}),
            studyPopulationSource: defineFilter(ESD.studyPopulationSource, {delimiter: "|"}),
            exposureMeasure: defineFilter(ESD.exposureMeasure, {delimiter: "|"}),
            exposureRoute: defineFilter(ESD.exposureRoute, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(ESD.studyCitation, {on_click_event: "study"}),
            studyIdentifier: defineTable(ESD.studyIdentifier, {on_click_event: "study"}),
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
        DASHBOARDS: [
            {
                id: "epi-sd-study-design-vs-system-effect",
                label: "study design vs. system & effect",
                x_axis: "study-design",
                y_axis: "system+effect",
                filters: ["study-citation", "exposure-measured"],
                table_fields: [
                    "study-citation",
                    "study-design",
                    "exposure-measured",
                    "system",
                    "effect",
                ],
            },
            {
                id: "epi-sd-exposure-vs-system-effect",
                label: "exposure vs. system & effect",
                x_axis: "exposure-measured",
                y_axis: "system+effect",
                filters: ["study-citation", "exposure-metric"],
                table_fields: ["study-citation", "exposure-name", "system", "effect"],
            },
            {
                id: "epi-sd-exposure-route-vs-system-effect",
                label: "exposure route vs. system & effect",
                x_axis: "exposure-route",
                y_axis: "system+effect",
                filters: ["study-citation", "exposure-measured"],
                table_fields: ["study-citation", "exposure-name", "system", "effect"],
            },
            {
                id: "epi-sd-exposure-metric-vs-system-effect",
                label: "exposure metric vs. system & effect",
                x_axis: "exposure-metric",
                y_axis: "system+effect",
                filters: ["study-citation", "exposure-measured"],
                table_fields: ["study-citation", "exposure-name", "system", "effect"],
            },
            {
                id: "epi-sd-study-pop-source-vs-system-effect",
                label: "study population source vs. system & effect",
                x_axis: "study-pop-source",
                y_axis: "system+effect",
                filters: ["study-citation", "exposure-measured"],
                table_fields: ["study-citation", "exposure-name", "system", "effect"],
            },
            {
                id: "epi-sd-study-citation-vs-system-effect",
                label: "study citation vs. system & effect",
                x_axis: "study-citation",
                y_axis: "system+effect",
                filters: ["study-citation", "exposure-measured"],
                table_fields: ["study-citation", "exposure-name", "system", "effect"],
            },
            {
                id: "epi-sd-study-citation-vs-system",
                label: "study citation vs. system",
                x_axis: "study-citation",
                y_axis: "system",
                filters: ["study-citation", "exposure-measured"],
                table_fields: ["study-citation", "exposure-name", "system", "effect"],
            },
        ],
    };
ESDSettings.DASHBOARDS = [
    {
        id: "epi-sd-study-design-vs-system-effect",
        label: "study design vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.studyDesign.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-exposure-vs-system-effect",
        label: "exposure vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.exposureName.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-measured-metric-vs-system-effect",
        label: "chemical & metric vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.exposureMeasureMetric.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-exposure-route-vs-system-effect",
        label: "exposure route vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.exposureRoute.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-exposure-metric-vs-system-effect",
        label: "exposure metric vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.exposureMetric.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-study-pop-source-vs-system-effect",
        label: "study population source vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.studyPopulationSource.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-study-citation-vs-system-effect",
        label: "study citation vs. system & effect",
        x_axis: ESDSettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: ESDSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
            ESDSettings.TABLE_FIELDS.system.id,
            ESDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "epi-sd-study-citation-vs-system",
        label: "study citation vs. system",
        x_axis: ESDSettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: ESDSettings.AXIS_OPTIONS.system.id,
        filters: [
            ESDSettings.FILTER_OPTIONS.studyCitation.id,
            ESDSettings.FILTER_OPTIONS.exposureMeasure.id,
        ],
        table_fields: [
            ESDSettings.TABLE_FIELDS.studyCitation.id,
            ESDSettings.TABLE_FIELDS.exposureName.id,
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
        studyDesign: defineProps("studyDesign", "study design", "study design"),
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
            studyDesign: defineFilter(ER.studyDesign),
            exposureRoute: defineFilter(ER.exposureRoute, {delimiter: "|"}),
            exposureMeasure: defineFilter(ER.exposureMeasure),
            exposureMetric: defineFilter(ER.exposureMetric),
            system: defineFilter(ER.system),
            effect: defineFilter(ER.effect),
            effectSubtype: defineFilter(ER.effectSubtype),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(ER.studyCitation, {on_click_event: "study"}),
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
        id: "epi-res-study-design-vs-system-effect",
        label: "study design vs. system & effect",
        x_axis: ERSettings.AXIS_OPTIONS.studyDesign.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.outcomeName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "epi-res-measured-metric-vs-system-effect",
        label: "chemical & metric vs. system & effect",
        x_axis: ERSettings.AXIS_OPTIONS.exposureMeasureMetric.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "epi-res-exposure-route-vs-system-effect",
        label: "exposure route vs. system & effect",
        x_axis: ERSettings.AXIS_OPTIONS.exposureRoute.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "epi-res-exposure-metric-vs-system-effect",
        label: "exposure metric vs. system & effect",
        x_axis: ERSettings.AXIS_OPTIONS.exposureMetric.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "epi-res-study-pop-source-vs-system-effect",
        label: "study population source vs. system & effect",
        x_axis: ERSettings.AXIS_OPTIONS.studyPopulationSource.id,
        y_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "epi-res-study-citation-vs-system-effect",
        label: "study citation vs. system & effect",
        x_axis: ERSettings.AXIS_OPTIONS.systemEffect.id,
        y_axis: ERSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
    {
        id: "epi-res-study-citation-vs-system",
        label: "study citation vs. system",
        x_axis: ERSettings.AXIS_OPTIONS.system.id,
        y_axis: ERSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            ERSettings.FILTER_OPTIONS.studyCitation.id,
            ERSettings.FILTER_OPTIONS.exposureMetric.id,
        ],
        table_fields: [
            ERSettings.TABLE_FIELDS.studyCitation.id,
            ERSettings.TABLE_FIELDS.exposureName.id,
            ERSettings.TABLE_FIELDS.resultName.id,
        ],
    },
];

export {ESDSettings, ERSettings};
