import {
    COLORS,
    defineAxis,
    defineFilter,
    defineMultiAxis,
    defineProps,
    defineTable,
} from "./shared";

// EcSD = eco study design
const EcSD = {
        studyId: defineProps("studyId", "Study ID", "study_id"),
        PMID: defineProps("PMID", "PubMed", "pubmed_id"),
        HERO: defineProps("HERO", "HERO", "hero_id"),
        DOI: defineProps("DOI", "DOI", "doi"),
        shortCitation: defineProps("shortCitation", "Study citation", "short_citation"),
        fullCitation: defineProps("fullCitation", "Full Citation", "full_citation"),
        designs: defineProps("designs", "Design", "designs"),
        designTypes: defineProps("designTypes", "Design type", "design_types"),
        studySettings: defineProps("studySettings", "Study Setting", "study_settings"),
        countries: defineProps("countries", "Countries", "countries"),
        states: defineProps("states", "States", "states"),
        ecoregions: defineProps("ecoregions", "Ecoregions", "ecoregions"),
        habitats: defineProps("habitats", "Habitats", "habitats"),
        climates: defineProps("climates", "Climates", "climates"),
        causes: defineProps("causes", "Causes", "causes"),
        effects: defineProps("effects", "Effects", "effects"),
    },
    EcSDSettings = {
        AXIS_OPTIONS: {
            shortCitation: defineAxis(EcSD.shortCitation),
            designs: defineAxis(EcSD.designs, {delimiter: "|"}),
            designTypes: defineAxis(EcSD.designTypes, {delimiter: "|"}),
            studySettings: defineAxis(EcSD.studySettings, {delimiter: "|"}),
            countries: defineAxis(EcSD.countries, {delimiter: "|"}),
            states: defineAxis(EcSD.states, {delimiter: "|"}),
            ecoregions: defineAxis(EcSD.ecoregions, {delimiter: "|"}),
            habitats: defineAxis(EcSD.habitats, {delimiter: "|"}),
            climates: defineAxis(EcSD.climates, {delimiter: "|"}),
            causes: defineAxis(EcSD.causes, {delimiter: "|"}),
            effects: defineAxis(EcSD.effects, {delimiter: "|"}),
        },
        FILTER_OPTIONS: {
            shortCitation: defineFilter(EcSD.shortCitation, {on_click_event: "study"}),
            designs: defineFilter(EcSD.designs, {delimiter: "|"}),
            designTypes: defineFilter(EcSD.designTypes, {delimiter: "|"}),
            studySettings: defineFilter(EcSD.studySettings, {delimiter: "|"}),
            countries: defineFilter(EcSD.countries, {delimiter: "|"}),
            states: defineFilter(EcSD.states, {delimiter: "|"}),
            ecoregions: defineFilter(EcSD.ecoregions, {delimiter: "|"}),
            habitats: defineFilter(EcSD.habitats, {delimiter: "|"}),
            climates: defineFilter(EcSD.climates, {delimiter: "|"}),
            causes: defineFilter(EcSD.causes, {delimiter: "|"}),
            effects: defineFilter(EcSD.effects, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            shortCitation: defineTable(EcSD.shortCitation, {on_click_event: "study"}),
            PMID: defineTable(EcSD.PMID, {on_click_event: "pubmed"}),
            HERO: defineTable(EcSD.HERO, {on_click_event: "hero"}),
            DOI: defineTable(EcSD.DOI),
            fullCitation: defineTable(EcSD.fullCitation),
            designs: defineTable(EcSD.designs, {delimiter: "|"}),
            designTypes: defineTable(EcSD.designTypes, {delimiter: "|"}),
            studySettings: defineTable(EcSD.studySettings, {delimiter: "|"}),
            countries: defineTable(EcSD.countries, {delimiter: "|"}),
            states: defineTable(EcSD.states, {delimiter: "|"}),
            ecoregions: defineTable(EcSD.ecoregions, {delimiter: "|"}),
            habitats: defineTable(EcSD.habitats, {delimiter: "|"}),
            climates: defineTable(EcSD.climates, {delimiter: "|"}),
            causes: defineTable(EcSD.causes, {delimiter: "|"}),
            effects: defineTable(EcSD.effects, {delimiter: "|"}),
        },
    };
EcSDSettings.DASHBOARDS = [
    {
        id: "cause-effect",
        label: "Cause vs Effect",
        upperColor: COLORS.green,
        x_axis: EcSDSettings.AXIS_OPTIONS.causes.id,
        y_axis: EcSDSettings.AXIS_OPTIONS.effects.id,
        filters: [
            EcSDSettings.FILTER_OPTIONS.shortCitation.id,
            EcSDSettings.FILTER_OPTIONS.designTypes.id,
            EcSDSettings.FILTER_OPTIONS.habitats.id,
        ],
        table_fields: [
            EcSDSettings.TABLE_FIELDS.shortCitation.id,
            EcSDSettings.TABLE_FIELDS.designTypes.id,
            EcSDSettings.TABLE_FIELDS.studySettings.id,
            EcSDSettings.TABLE_FIELDS.countries.id,
            EcSDSettings.TABLE_FIELDS.habitats.id,
            EcSDSettings.TABLE_FIELDS.causes.id,
            EcSDSettings.TABLE_FIELDS.effects.id,
        ],
    },
    {
        id: "cause-citation",
        label: "Cause vs Study Citation",
        upperColor: COLORS.purple,
        x_axis: EcSDSettings.AXIS_OPTIONS.causes.id,
        y_axis: EcSDSettings.AXIS_OPTIONS.shortCitation.id,
        filters: [
            EcSDSettings.FILTER_OPTIONS.designTypes.id,
            EcSDSettings.FILTER_OPTIONS.habitats.id,
            EcSDSettings.FILTER_OPTIONS.effects.id,
        ],
        table_fields: [
            EcSDSettings.TABLE_FIELDS.shortCitation.id,
            EcSDSettings.TABLE_FIELDS.designTypes.id,
            EcSDSettings.TABLE_FIELDS.studySettings.id,
            EcSDSettings.TABLE_FIELDS.countries.id,
            EcSDSettings.TABLE_FIELDS.habitats.id,
            EcSDSettings.TABLE_FIELDS.causes.id,
            EcSDSettings.TABLE_FIELDS.effects.id,
        ],
    },
    {
        id: "effect-citation",
        label: "Effect vs Study Citation",
        upperColor: COLORS.orange,
        x_axis: EcSDSettings.AXIS_OPTIONS.effects.id,
        y_axis: EcSDSettings.AXIS_OPTIONS.shortCitation.id,
        filters: [
            EcSDSettings.FILTER_OPTIONS.designTypes.id,
            EcSDSettings.FILTER_OPTIONS.habitats.id,
            EcSDSettings.FILTER_OPTIONS.causes.id,
        ],
        table_fields: [
            EcSDSettings.TABLE_FIELDS.shortCitation.id,
            EcSDSettings.TABLE_FIELDS.designTypes.id,
            EcSDSettings.TABLE_FIELDS.studySettings.id,
            EcSDSettings.TABLE_FIELDS.countries.id,
            EcSDSettings.TABLE_FIELDS.habitats.id,
            EcSDSettings.TABLE_FIELDS.causes.id,
            EcSDSettings.TABLE_FIELDS.effects.id,
        ],
    },
];

// EcR = eco results
const EcR = {
        studyId: defineProps("studyId", "Study ID", "study"),
        studyPMID: defineProps("studyPMID", "PubMed ID", "study-pmid"),
        studyHERO: defineProps("studyHERO", "HERO ID", "study-hero"),
        studyDOI: defineProps("studyDOI", "DOI", "study-doi"),
        studyCitation: defineProps("studyCitation", "Study citation", "study-short_citation"),
        studyFullCitation: defineProps(
            "studyFullCitation",
            "Study full citation",
            "study-full_citation"
        ),
        studyCOIReported: defineProps(
            "studyCOIReported",
            "Study COI Reported",
            "study-coi_reported"
        ),
        studyCOIDetails: defineProps("studyCOIDetails", "Study COI details", "study-coi_details"),
        studyFundingSource: defineProps(
            "studyFundingSource",
            "Study Funding Source",
            "study-funding_source"
        ),
        studyIdentifier: defineProps(
            "studyIdentifier",
            "Study Identifier",
            "study-study_identifier"
        ),
        studyContactAuthor: defineProps(
            "studyContactAuthor",
            "Study Contact Author",
            "study-contact_author"
        ),
        studyAskAuthor: defineProps("studyAskAuthor", "Study Ask Author", "study-ask_author"),
        studyPublished: defineProps("studyPublished", "Study Published", "study-published"),
        studySummary: defineProps("studySummary", "Study Summary", "study-summary"),
        designName: defineProps("designName", "Design Name", "design-name"),
        designType: defineProps("designType", "Design Type", "design-design_type"),
        designSetting: defineProps("designSetting", "Design Study Setting", "design-study_setting"),
        designCountries: defineProps("designCountries", "Design Countries", "design-countries"),
        designStates: defineProps("designStates", "Design States", "design-states"),
        designEcoregions: defineProps("designEcoregions", "Design Ecoregions", "design-ecoregions"),
        designHabitats: defineProps("designHabitats", "Design Habitats", "design-habitats"),
        designHabitatsReported: defineProps(
            "designHabitatsReported",
            "Design Habitats as reported",
            "design-habitats_as_reported"
        ),
        designClimates: defineProps("designClimates", "Design Climates", "design-climates"),
        designClimatesReported: defineProps(
            "designClimatesReported",
            "Design Climates as reported",
            "design-climatesas_reported"
        ),
        designComments: defineProps("designComments", "Design Comments", "design-comments"),
        causeName: defineProps("causeName", "Cause Name", "cause-name"),
        causeTerm: defineProps("causeTerm", "Cause Term", "cause-term"),
        causeBioOrg: defineProps(
            "causeBioOrg",
            "Cause Biological Organization",
            "cause-biological_organization"
        ),
        causeSpecies: defineProps("causeSpecies", "Cause Species", "cause-species"),
        causeLevel: defineProps("causeLevel", "Cause Level", "cause-level"),
        causeLevelValue: defineProps("causeLevelValue", "Cause Level Value", "cause-level_value"),
        causeLevelUnits: defineProps("causeLevelUnits", "Cause Level Units", "cause-level_units"),
        causeDuration: defineProps("causeDuration", "Cause Duration", "cause-duration"),
        causeDurationUnits: defineProps(
            "causeDurationUnits",
            "Cause Duration Units",
            "cause-duration_units"
        ),
        causeExposure: defineProps("causeExposure", "Cause Exposure", "cause-exposure"),
        causeExposureValue: defineProps(
            "causeExposureValue",
            "Cause Exposure Value",
            "cause-exposure_value"
        ),
        causeExposureUnits: defineProps(
            "causeExposureUnits",
            "Cause Exposure Units",
            "cause-exposure_units"
        ),
        causeAsReported: defineProps("causeAsReported", "Cause As Reported", "cause-as_reported"),
        causeComments: defineProps("causeComments", "Cause Comments", "cause-comments"),
        effectName: defineProps("effectName", "Effect Name", "effect-name"),
        effectTerm: defineProps("effectTerm", "Effect Term", "effect-term"),
        effectBioOrg: defineProps(
            "effectBioOrg",
            "Effect Biological Organization",
            "effect-biological_organization"
        ),
        effectSpecies: defineProps("effectSpecies", "Effect Species", "effect-species"),
        effectUnits: defineProps("effectUnits", "Effect Units", "effect-units"),
        effectAsReported: defineProps(
            "effectAsReported",
            "Effect As Reported",
            "effect-as_reported"
        ),
        effectComments: defineProps("effectComments", "Effect Comments", "effect-comments"),
        resultName: defineProps("resultName", "Result Name", "result-name"),
        resultSortOrder: defineProps("resultSortOrder", "Result Sort Order", "result-sort_order"),
        resultRelDir: defineProps(
            "resultRelDir",
            "Result Relationship Direction",
            "result-relationship_direction"
        ),
        resultRelComment: defineProps(
            "resultRelComment",
            "Result Relationship Comment",
            "result-relationship_comment"
        ),
        resultMeasureType: defineProps(
            "resultMeasureType",
            "Result Measure Type",
            "result-measure_type"
        ),
        resultMeasuredValue: defineProps(
            "resultMeasuredValue",
            "Result Measured Value",
            "result-measure_value"
        ),
        resultDerivedValue: defineProps(
            "resultDerivedValue",
            "Result derived value",
            "result-derived_value"
        ),
        resultSampleSize: defineProps(
            "resultSampleSize",
            "Result Sample Size",
            "result-sample_size"
        ),
        resultVariability: defineProps(
            "resultVariability",
            "Result Variability",
            "result-variability"
        ),
        resultLowVariability: defineProps(
            "resultLowVariability",
            "Result Low Variability",
            "result-low_variability"
        ),
        resultUpperVariability: defineProps(
            "resultUpperVariability",
            "Result Upper Variability",
            "result-upper_variability"
        ),
        resultModifyingFactors: defineProps(
            "resultModifyingFactors",
            "Result Modifying Factors",
            "result-modifying_factors"
        ),
        resultModifyingFactorsComment: defineProps(
            "resultModifyingFactorsComment",
            "Result Modifying Factors Comment",
            "result-modifying_factors_comment"
        ),
        resultStatisticalSigType: defineProps(
            "resultStatisticalSigType",
            "Result Statistical Sig Type",
            "result-statistical_sig_type"
        ),
        resultStatisticalSigValue: defineProps(
            "resultStatisticalSigValue",
            "Result Statistical Sig Value",
            "result-statistical_sig_value"
        ),
        resultComments: defineProps("resultComments", "Result Comments", "result-comments"),
    },
    EcRSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(EcR.studyCitation),
            designName: defineAxis(EcR.designName),
            designType: defineAxis(EcR.designType),
            designSetting: defineAxis(EcR.designSetting),
            designCountries: defineAxis(EcR.designCountries, {delimiter: "|"}),
            designEcoregions: defineAxis(EcR.designEcoregions, {delimiter: "|"}),
            designHabitats: defineAxis(EcR.designHabitats, {delimiter: "|"}),
            designClimates: defineAxis(EcR.designClimates, {delimiter: "|"}),
            causeName: defineAxis(EcR.causeName),
            causeTerm: defineAxis(EcR.causeTerm),
            causeSpecies: defineAxis(EcR.causeSpecies),
            causeDuration: defineAxis(EcR.causeDuration),
            causeExposure: defineAxis(EcR.causeExposure),
            effectName: defineAxis(EcR.effectName),
            effectTerm: defineAxis(EcR.effectTerm),
            effectSpecies: defineAxis(EcR.effectSpecies),
            causeEffect: defineMultiAxis(
                [EcR.causeName, EcR.effectName],
                "causeEffect",
                "Cause & Effect"
            ),
            resultMeasuredValue: defineAxis(EcR.resultMeasuredValue),
            resultRelDir: defineAxis(EcR.resultRelDir),
            resultDerivedValue: defineAxis(EcR.resultDerivedValue),
            resultSampleSize: defineAxis(EcR.resultSampleSize),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(EcR.studyCitation, {on_click_event: "study"}),
            designName: defineFilter(EcR.designName),
            designType: defineFilter(EcR.designType),
            designSetting: defineFilter(EcR.designSetting),
            designCountries: defineFilter(EcR.designCountries, {delimiter: "|"}),
            designStates: defineFilter(EcR.designStates, {delimiter: "|"}),
            designEcoregions: defineFilter(EcR.designEcoregions, {delimiter: "|"}),
            designHabitats: defineFilter(EcR.designHabitats, {delimiter: "|"}),
            designClimates: defineFilter(EcR.designClimates, {delimiter: "|"}),
            causeName: defineFilter(EcR.causeName),
            causeTerm: defineFilter(EcR.causeTerm),
            causeSpecies: defineFilter(EcR.causeSpecies),
            effectName: defineFilter(EcR.effectName),
            effectTerm: defineFilter(EcR.effectTerm),
            effectSpecies: defineFilter(EcR.effectSpecies),
            resultName: defineFilter(EcR.resultName),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(EcR.studyCitation, {on_click_event: "study"}),
            studyFullCitation: defineTable(EcR.studyFullCitation),
            studySummary: defineTable(EcR.studySummary),
            designName: defineTable(EcR.designName, {on_click_event: "eco_design"}),
            designType: defineTable(EcR.designType),
            designSetting: defineTable(EcR.designSetting),
            designCountries: defineTable(EcR.designCountries, {delimiter: "|"}),
            designStates: defineTable(EcR.designStates, {delimiter: "|"}),
            designEcoregions: defineTable(EcR.designEcoregions, {delimiter: "|"}),
            designHabitats: defineTable(EcR.designHabitats, {delimiter: "|"}),
            designHabitatsReported: defineTable(EcR.designHabitatsReported),
            designClimates: defineTable(EcR.designClimates, {delimiter: "|"}),
            designClimatesReported: defineTable(EcR.designClimatesReported),
            designComments: defineTable(EcR.designComments),
            causeName: defineTable(EcR.causeName),
            causeTerm: defineTable(EcR.causeTerm),
            causeBioOrg: defineTable(EcR.causeBioOrg),
            causeSpecies: defineTable(EcR.causeSpecies),
            causeLevel: defineTable(EcR.causeLevel),
            causeLevelUnits: defineTable(EcR.causeLevelUnits),
            causeDuration: defineTable(EcR.causeDuration),
            causeDurationUnits: defineTable(EcR.causeDurationUnits),
            causeExposure: defineTable(EcR.causeExposure),
            causeExposureUnits: defineTable(EcR.causeExposureUnits),
            causeAsReported: defineTable(EcR.causeAsReported),
            causeComments: defineTable(EcR.causeComments),
            effectName: defineTable(EcR.effectName),
            effectTerm: defineTable(EcR.effectTerm),
            effectSpecies: defineTable(EcR.effectSpecies),
            effectUnits: defineTable(EcR.effectUnits),
            effectAsReported: defineTable(EcR.effectAsReported),
            effectComments: defineTable(EcR.effectComments),
            resultName: defineTable(EcR.resultName),
            resultRelDir: defineTable(EcR.resultRelDir),
            resultRelComment: defineTable(EcR.resultRelComment),
            resultMeasureType: defineTable(EcR.resultMeasureType),
            resultMeasuredValue: defineTable(EcR.resultMeasuredValue),
            resultDerivedValue: defineTable(EcR.resultDerivedValue),
            resultSampleSize: defineTable(EcR.resultSampleSize),
            resultVariability: defineTable(EcR.resultVariability),
            resultLowVariability: defineTable(EcR.resultLowVariability),
            resultHUpperVariability: defineTable(EcR.resultUpperVariability),
            resultModifyingFactors: defineTable(EcR.resultModifyingFactors),
            resultModifyingFactorsComment: defineTable(EcR.resultModifyingFactorsComment),
            resultStatisticalSigType: defineTable(EcR.resultStatisticalSigType),
            resultStatisticalSigValue: defineTable(EcR.resultStatisticalSigValue),
            resultComments: defineTable(EcR.resultComments),
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
            EcRSettings.TABLE_FIELDS.designCountries.id,
            EcRSettings.TABLE_FIELDS.designStates.id,
            EcRSettings.TABLE_FIELDS.resultDerivedValue.id,
        ],
    },
    {
        id: "cause vs. reference",
        label: "cause vs. reference",
        upperColor: COLORS.green,
        x_axis: EcRSettings.AXIS_OPTIONS.causeName.id,
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
            EcRSettings.TABLE_FIELDS.designCountries.id,
            EcRSettings.TABLE_FIELDS.designStates.id,
            EcRSettings.TABLE_FIELDS.resultDerivedValue.id,
        ],
    },
    {
        id: "effect vs cause",
        label: "effect vs cause",
        upperColor: COLORS.orange,
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
            EcRSettings.TABLE_FIELDS.designCountries.id,
            EcRSettings.TABLE_FIELDS.designStates.id,
            EcRSettings.TABLE_FIELDS.resultDerivedValue.id,
        ],
    },
];

export {EcRSettings, EcSDSettings};
