import {
    defineProps,
    defineAxis,
    defineMultiAxis,
    defineFilter,
    defineTable,
    COLORS,
} from "./shared";

// DS = data schema
const DS = {
        studyId: defineProps("studyId", "Study ID", "study id"),
        studyShortCitation: defineProps(
            "studyShortCitation",
            "study short citation",
            "study short citation"
        ),
        evaluationDomainId: defineProps(
            "evaluationDomainId",
            "evaluation domain id",
            "evaluation domain id"
        ),
        evaluationDomainName: defineProps(
            "evaluationDomainName",
            "evaluation domain name",
            "evaluation domain name"
        ),
        evaluationMetricId: defineProps(
            "evaluationMetricId",
            "evaluation metric id",
            "evaluation metric id"
        ),
        evaluationMetricName: defineProps(
            "evaluationMetricName",
            "evaluation metric name",
            "evaluation metric name"
        ),
        evaluationMetricShortName: defineProps(
            "evaluationMetricShortName",
            "evaluation metric short name",
            "evaluation metric short name"
        ),
        evaluationId: defineProps("evaluationId", "evaluation id", "evaluation id"),
        evaluationLabel: defineProps("evaluationLabel", "evaluation label", "evaluation label"),
        evaluationValue: defineProps("evaluationValue", "evaluation value", "evaluation value"),
        evaluationBiasDirection: defineProps(
            "evaluationBiasDirection",
            "evaluation bias direction",
            "evaluation bias direction"
        ),
        evaluationNotes: defineProps("evaluationNotes", "evaluation notes", "evaluation notes"),
        evaluationSymbol: defineProps("evaluationSymbol", "evaluation symbol", "evaluation symbol"),
        evaluationText: defineProps("evaluationText", "evaluation text", "evaluation text"),
        evaluationDirectionText: defineProps(
            "evaluationDirectionText",
            "evaluation direction text",
            "evaluation direction text"
        ),
        evaluation: defineProps("evaluation", "evaluation", "evaluation"),
        id: defineProps("id", "id", "id"),
        studyTypes: defineProps("studyTypes", "Study Type", "study types"),
    },
    RobSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(DS.studyShortCitation),
            evaluation: defineAxis(DS.evaluation),
            domainMetric: defineMultiAxis(
                [DS.evaluationDomainName, DS.evaluationMetricShortName],
                "domainMetric",
                "Domain and Metric"
            ),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(DS.studyShortCitation, {on_click_event: "study id"}),
            studyTypes: defineFilter(DS.studyTypes, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(DS.studyShortCitation, {on_click_event: "study id"}),
            evaluationLabel: defineTable(DS.evaluationLabel),
            evaluation: defineTable(DS.evaluation),
            evaluationDirectionText: defineTable(DS.evaluationDirectionText),
            evaluationNotes: defineTable(DS.evaluationNotes),
        },
    };

RobSettings.DASHBOARDS = [
    {
        id: "short citation vs. domain & metric",
        label: "short citation vs. domain & metric",
        upperColor: COLORS.blue,
        x_axis: RobSettings.AXIS_OPTIONS.domainMetric.id,
        y_axis: RobSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            RobSettings.FILTER_OPTIONS.studyTypes.id,
            RobSettings.FILTER_OPTIONS.studyCitation.id,
        ],
        table_fields: [
            RobSettings.TABLE_FIELDS.studyCitation.id,
            RobSettings.TABLE_FIELDS.evaluationLabel.id,
            RobSettings.TABLE_FIELDS.evaluation.id,
            RobSettings.TABLE_FIELDS.evaluationDirectionText.id,
            RobSettings.TABLE_FIELDS.evaluationNotes.id,
        ],
    },
];

export {RobSettings};
