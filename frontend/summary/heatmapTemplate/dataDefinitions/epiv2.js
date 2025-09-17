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
        studyId: defineProps("studyId", "Study ID", "study_id"),
        PMID: defineProps("PMID", "PubMed ID", "PMID"),
        HERO: defineProps("HERO", "HERO ID", "HERO ID"),
        DOI: defineProps("DOI", "DOI", "DOI"),
        shortCitation: defineProps("shortCitation", "Study Citation", "short_citation"),
        fullCitation: defineProps("fullCitation", "Full Citation", "full_citation"),
        studyDesign: defineProps("studyDesign", "Study Design", "study_design"),
        designSummary: defineProps("designSummary", "Design Summary", "design_summary"),
        countries: defineProps("countries", "Countries", "countries"),
        designSource: defineProps("designSource", "Design Source", "design_source"),
        ageProfile: defineProps("ageProfile", "Age Profile", "age_profile"),
        participantN: defineProps("participantN", "Study Population N", "participant_n"),
        chemicalName: defineProps("chemicalName", "Chemical Name", "chemical_name"),
        exposureName: defineProps("exposureName", "Exposure Name", "exposure_name"),
        exposureMeasurementType: defineProps(
            "exposureMeasurementType",
            "Exposure Measurement Type",
            "exposure_measurement_type"
        ),
        exposureBiomonitoringMatrix: defineProps(
            "exposureBiomonitoringMatrix",
            "Exposure Biomonitoring Matrix",
            "exposure_biomonitoring_matrix"
        ),
        exposureRoute: defineProps("exposureRoute", "Exposure Route", "exposure_route"),
        outcomeSystem: defineProps("outcomeSystem", "System", "outcome_system"),
        outcomeEffect: defineProps("outcomeEffect", "Effect", "outcome_effect"),
        outcomeEndpoint: defineProps("outcomeEndpoint", "Endpoint", "outcome_endpoint"),
    },
    ESDv2Settings = {
        AXIS_OPTIONS: {
            shortCitation: defineAxis(ESD.shortCitation),
            countries: defineAxis(ESD.countries, {delimiter: "|"}),
            designSource: defineAxis(ESD.designSource, {delimiter: "|"}),
            studyDesign: defineAxis(ESD.studyDesign, {delimiter: "|"}),
            ageProfile: defineAxis(ESD.ageProfile, {delimiter: "|"}),
            chemicalName: defineAxis(ESD.chemicalName, {delimiter: "|"}),
            exposureName: defineAxis(ESD.exposureName, {delimiter: "|"}),
            exposureMeasurementType: defineAxis(ESD.exposureMeasurementType, {delimiter: "|"}),
            exposureBiomonitoringMatrix: defineAxis(ESD.exposureBiomonitoringMatrix, {
                delimiter: "|",
            }),
            exposureRoute: defineAxis(ESD.exposureRoute, {delimiter: "|"}),
            outcomeSystem: defineAxis(ESD.outcomeSystem, {delimiter: "|"}),
            outcomeEffect: defineAxis(ESD.outcomeEffect, {delimiter: "|"}),
            outcomeEndpoint: defineAxis(ESD.outcomeEndpoint, {delimiter: "|"}),
            outcomeSystemEffect: defineMultiAxis(
                [ESD.outcomeSystem, ESD.outcomeEffect],
                "outcomeSystemEffect",
                "Outcome System & Effect",
                {delimiter: "|"}
            ),
        },
        FILTER_OPTIONS: {
            shortCitation: defineFilter(ESD.shortCitation, {on_click_event: "study"}),
            countries: defineFilter(ESD.countries, {delimiter: "|"}),
            designSource: defineFilter(ESD.designSource, {delimiter: "|"}),
            studyDesign: defineFilter(ESD.studyDesign, {delimiter: "|"}),
            ageProfile: defineFilter(ESD.ageProfile, {delimiter: "|"}),
            chemicalName: defineFilter(ESD.chemicalName, {delimiter: "|"}),
            exposureName: defineFilter(ESD.exposureName, {delimiter: "|"}),
            exposureMeasurementType: defineFilter(ESD.exposureMeasurementType, {delimiter: "|"}),
            exposureBiomonitoringMatrix: defineFilter(ESD.exposureBiomonitoringMatrix, {
                delimiter: "|",
            }),
            exposureRoute: defineFilter(ESD.exposureRoute, {delimiter: "|"}),
            outcomeSystem: defineFilter(ESD.outcomeSystem, {delimiter: "|"}),
            outcomeEffect: defineFilter(ESD.outcomeEffect, {delimiter: "|"}),
            outcomeEndpoint: defineFilter(ESD.outcomeEndpoint, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            shortCitation: defineTable(ESD.shortCitation, {on_click_event: "study"}),
            fullCitation: defineTable(ESD.fullCitation),
            countries: defineTable(ESD.countries, {delimiter: "|"}),
            designSource: defineTable(ESD.designSource, {delimiter: "|"}),
            designSummary: defineTable(ESD.designSummary, {delimiter: "|"}),
            studyDesign: defineTable(ESD.studyDesign, {delimiter: "|"}),
            ageProfile: defineTable(ESD.ageProfile, {delimiter: "|"}),
            participantN: defineTable(ESD.participantN, {delimter: "|"}),
            chemicalName: defineTable(ESD.chemicalName, {delimiter: "|"}),
            exposureName: defineTable(ESD.exposureName, {delimiter: "|"}),
            exposureMeasurementType: defineTable(ESD.exposureMeasurementType, {delimiter: "|"}),
            exposureBiomonitoringMatrix: defineTable(ESD.exposureBiomonitoringMatrix, {
                delimiter: "|",
            }),
            exposureRoute: defineTable(ESD.exposureRoute, {delimiter: "|"}),
            outcomeSystem: defineTable(ESD.outcomeSystem, {delimiter: "|"}),
            outcomeEffect: defineTable(ESD.outcomeEffect, {delimiter: "|"}),
            outcomeEndpoint: defineTable(ESD.outcomeEndpoint, {delimiter: "|"}),
        },
    };
ESDv2Settings.DASHBOARDS = [
    {
        id: "system_vs_design",
        label: "Outcome System by Study Design",
        upperColor: COLORS.green,
        x_axis: ESDv2Settings.AXIS_OPTIONS.studyDesign.id,
        y_axis: ESDv2Settings.AXIS_OPTIONS.outcomeSystem.id,
        filters: [
            ESDv2Settings.FILTER_OPTIONS.shortCitation.id,
            ESDv2Settings.FILTER_OPTIONS.designSource.id,
            ESDv2Settings.FILTER_OPTIONS.ageProfile.id,
            ESDv2Settings.FILTER_OPTIONS.chemicalName.id,
        ],
        table_fields: [
            ESDv2Settings.TABLE_FIELDS.shortCitation.id,
            ESDv2Settings.TABLE_FIELDS.fullCitation.id,
            ESDv2Settings.TABLE_FIELDS.countries.id,
            ESDv2Settings.TABLE_FIELDS.designSource.id,
            ESDv2Settings.TABLE_FIELDS.ageProfile.id,
            ESDv2Settings.TABLE_FIELDS.chemicalName.id,
            ESDv2Settings.TABLE_FIELDS.exposureName.id,
            ESDv2Settings.TABLE_FIELDS.outcomeSystem.id,
            ESDv2Settings.TABLE_FIELDS.outcomeEffect.id,
            ESDv2Settings.TABLE_FIELDS.outcomeEndpoint.id,
        ],
    },
    {
        id: "system_vs_chemical",
        label: "Outcome System by Chemical",
        upperColor: COLORS.purple,
        x_axis: ESDv2Settings.AXIS_OPTIONS.chemicalName.id,
        y_axis: ESDv2Settings.AXIS_OPTIONS.outcomeSystem.id,
        filters: [
            ESDv2Settings.FILTER_OPTIONS.shortCitation.id,
            ESDv2Settings.FILTER_OPTIONS.studyDesign.id,
            ESDv2Settings.FILTER_OPTIONS.designSource.id,
            ESDv2Settings.FILTER_OPTIONS.ageProfile.id,
        ],
        table_fields: [
            ESDv2Settings.TABLE_FIELDS.shortCitation.id,
            ESDv2Settings.TABLE_FIELDS.fullCitation.id,
            ESDv2Settings.TABLE_FIELDS.countries.id,
            ESDv2Settings.TABLE_FIELDS.designSource.id,
            ESDv2Settings.TABLE_FIELDS.ageProfile.id,
            ESDv2Settings.TABLE_FIELDS.chemicalName.id,
            ESDv2Settings.TABLE_FIELDS.exposureName.id,
            ESDv2Settings.TABLE_FIELDS.outcomeSystem.id,
            ESDv2Settings.TABLE_FIELDS.outcomeEffect.id,
            ESDv2Settings.TABLE_FIELDS.outcomeEndpoint.id,
        ],
    },
];

// ER = epi results
const ER = {
        /* eslint-disable */
        studyId: defineProps("studyId", "Study ID", "study-id"),
        studyHeroId: defineProps("studyHeroId", "HERO ID", "study-hero_id"),
        studyPubmedId: defineProps("studyPubmedId", "PMID", "study-pubmed_id"),
        studyDoi: defineProps("studyDoi", "DOI", "study-doi"),
        studyShortCitation: defineProps(
            "studyShortCitation",
            "Short Citation",
            "study-short_citation"
        ),
        studyFullCitation: defineProps("studyFullCitation", "Full Citation", "study-full_citation"),
        studyStudyIdentifier: defineProps(
            "studyStudyIdentifier",
            "Study Identifier",
            "study-study_identifier"
        ),
        designPk: defineProps("designPk", "Design ID", "design-pk"),
        designSummary: defineProps("designSummary", "Design Summary", "design-summary"),
        designStudyName: defineProps("designStudyName", "Study Name", "design-study_name"),
        studyDesign: defineProps("studyDesign", "Study Design", "design-study_design"),
        designSource: defineProps("designSource", "Source", "design-source"),
        designAgeProfile: defineProps("designAgeProfile", "Age Profile", "design-age_profile"),
        designAgeDescription: defineProps(
            "designAgeDescription",
            "Age Description",
            "design-age_description"
        ),
        designSex: defineProps("designSex", "Sex", "design-sex"),
        designRace: defineProps("designRace", "Race", "design-race"),
        designParticipantN: defineProps(
            "designParticipantN",
            "Participant N",
            "design-participant_n"
        ),
        designYearsEnrolled: defineProps(
            "designYearsEnrolled",
            "Years Enrolled",
            "design-years_enrolled"
        ),
        designYearsFollowup: defineProps(
            "designYearsFollowup",
            "Years Follow up",
            "design-years_followup"
        ),
        designCountries: defineProps("designCountries", "Countries", "design-countries"),
        designRegion: defineProps("designRegion", "Region", "design-region"),
        designCriteria: defineProps("designCriteria", "Criteria", "design-criteria"),
        designSusceptibility: defineProps(
            "designSusceptibility",
            "Susceptibility",
            "design-susceptibility"
        ),
        chemicalPk: defineProps("chemicalPk", "Chemical ID", "chemical-pk"),
        chemicalName: defineProps("chemicalName", "Chemical Name", "chemical-name"),
        chemicalDTSXID: defineProps("chemicalDTSXID", "DTSXID", "chemical-DTSXID"),
        exposurePk: defineProps("exposurePk", "Exposure ID", "exposure-pk"),
        exposureName: defineProps("exposureName", "Exposure Name", "exposure-name"),
        exposureMeasurementType: defineProps(
            "exposureMeasurementType",
            "Exposure Measurement Type",
            "exposure-measurement_type"
        ),
        exposureBiomonitoringMatrix: defineProps(
            "exposureBiomonitoringMatrix",
            "Exposure Biomonitoring Matrix",
            "exposure-biomonitoring_matrix"
        ),
        exposureBiomonitoringSource: defineProps(
            "exposureBiomonitoringSource",
            "Exposure Biomonitoring Source",
            "exposure-biomonitoring_source"
        ),
        exposureMeasurementTiming: defineProps(
            "exposureMeasurementTiming",
            "Exposure Measurement Timing",
            "exposure-measurement_timing"
        ),
        exposureRoute: defineProps(
            "exposureExposureRoute",
            "Exposure Route",
            "exposure-exposure_route"
        ),
        exposureMeasurementMethod: defineProps(
            "exposureMeasurementMethod",
            "Exposure Measurement Method",
            "exposure-measurement_method"
        ),
        exposureLevelPk: defineProps("exposureLevelPk", "Exposure Level ID", "exposure_level-pk"),
        exposureLevelName: defineProps(
            "exposureLevelName",
            "Exposure Level Name",
            "exposure_level-name"
        ),
        exposureLevelSubPopulation: defineProps(
            "exposureLevelSubPopulation",
            "Exposure Level Supopulation",
            "exposure_level-sub_population"
        ),
        exposureLevelMedian: defineProps(
            "exposureLevelMedian",
            "Exposure Level Median",
            "exposure_level-median"
        ),
        exposureLevelMean: defineProps(
            "exposureLevelMean",
            "Exposure Level Mean",
            "exposure_level-mean"
        ),
        exposureLevelVariance: defineProps(
            "exposureLevelVariance",
            "Exposure Level Variance",
            "exposure_level-variance"
        ),
        exposureLevelVarianceType: defineProps(
            "exposureLevelVarianceType",
            "Exposure Level Variance Type",
            "exposure_level-variance_type"
        ),
        exposureLevelUnits: defineProps(
            "exposureLevelUnits",
            "Exposure Level Units",
            "exposure_level-units"
        ),
        exposureLevelCiLcl: defineProps(
            "exposureLevelCiLcl",
            "Exposure Level Lower CI",
            "exposure_level-ci_lcl"
        ),
        exposureLevelPercentile25: defineProps(
            "exposureLevelPercentile25",
            "Exposure Level P25",
            "exposure_level-percentile_25"
        ),
        exposureLevelPercentile75: defineProps(
            "exposureLevelPercentile75",
            "Exposure Level P75",
            "exposure_level-percentile_75"
        ),
        exposureLevelCiUcl: defineProps(
            "exposureLevelCiUcl",
            "Expsoure Level Upper CI",
            "exposure_level-ci_ucl"
        ),
        exposureLevelCiType: defineProps(
            "exposureLevelCiType",
            "Exposure Level CI Type",
            "exposure_level-ci_type"
        ),
        exposureLevelNegligibleExposure: defineProps(
            "exposureLevelNegligibleExposure",
            "Exposure Level Negligible Exposure",
            "exposure_level-negligible_exposure"
        ),
        outcomePk: defineProps("outcomePk", "Outcome ID", "outcome-pk"),
        outcomeSystem: defineProps("outcomeSystem", "Outcome System", "outcome-system"),
        outcomeEffect: defineProps("outcomeEffect", "Outcome Effect", "outcome-effect"),
        outcomeEffectDetail: defineProps(
            "outcomeEffectDetail",
            "Outcome Effect Detail",
            "outcome-effect_detail"
        ),
        outcomeEndpoint: defineProps("outcomeEndpoint", "Outcome Endpoint", "outcome-endpoint"),
        dataExtractionPk: defineProps("dataExtractionPk", "Data ID", "data_extraction-pk"),
        dataExtractionSubPopulation: defineProps(
            "dataExtractionSubPopulation",
            "Data Subpopulation",
            "data_extraction-sub_population"
        ),
        dataExtractionOutcomeMeasurementTiming: defineProps(
            "dataExtractionOutcomeMeasurementTiming",
            "Data Measurement Timing",
            "dataExtractionOutcomeMeasurementTiming"
        ),
        dataExtractionEffectEstimateType: defineProps(
            "dataExtractionEffectEstimateType",
            "Data Estimate Type",
            "data_extraction-effect_estimate_type"
        ),
        dataExtractionEffectEstimate: defineProps(
            "dataExtractionEffectEstimate",
            "Data Estimate",
            "data_extraction-effect_estimate"
        ),
        dataExtractionCiLcl: defineProps(
            "dataExtractionCiLcl",
            "Data Lower CI",
            "data_extraction-ci_lcl"
        ),
        dataExtractionCiUcl: defineProps(
            "dataExtractionCiUcl",
            "Data Upper CI",
            "data_extraction-ci_ucl"
        ),
        dataExtractionCiType: defineProps(
            "dataExtractionCiType",
            "Data CI Type",
            "data_extraction-ci_type"
        ),
        dataExtractionUnits: defineProps(
            "dataExtractionUnits",
            "Data Units",
            "data_extraction-units"
        ),
        dataExtractionVarianceType: defineProps(
            "dataExtractionVarianceType",
            "Data Variance Type",
            "data_extraction-variance_type"
        ),
        dataExtractionVariance: defineProps(
            "dataExtractionVariance",
            "Data Variance",
            "data_extraction-variance"
        ),
        dataExtractionN: defineProps("dataExtractionN", "Data N", "data_extraction-n"),
        dataExtractionPValue: defineProps(
            "dataExtractionPValue",
            "Data P-Value",
            "data_extraction-p_value"
        ),
        dataExtractionSignificant: defineProps(
            "dataExtractionSignificant",
            "Data Significance",
            "data_extraction-significant"
        ),
        dataExtractionGroup: defineProps(
            "dataExtractionGroup",
            "Data Group",
            "data_extraction-group"
        ),
        dataExtractionExposureRank: defineProps(
            "dataExtractionExposureRank",
            "Data Exposure Rank",
            "data_extraction-exposure_rank"
        ),
        dataExtractionExposureTransform: defineProps(
            "dataExtractionExposureTransform",
            "Data Exposure Transform",
            "data_extraction-exposure_transform"
        ),
        dataExtractionOutcomeTransform: defineProps(
            "dataExtractionOutcomeTransform",
            "Data Outcome Transform",
            "data_extraction-outcome_transform"
        ),
        dataExtractionConfidence: defineProps(
            "dataExtractionConfidence",
            "Data Confidence",
            "data_extraction-confidence"
        ),
        dataExtractionDataLocation: defineProps(
            "dataExtractionDataLocation",
            "Data Location",
            "data_extraction-data_location"
        ),
        dataExtractionEffectDescription: defineProps(
            "dataExtractionEffectDescription",
            "Data Effect Description",
            "data_extraction-effect_description"
        ),
        dataExtractionStatisticalMethod: defineProps(
            "dataExtractionStatisticalMethod",
            "Data Statistical Method",
            "data_extraction-statistical_method"
        ),
        adjustmentFactorPk: defineProps(
            "adjustmentFactorPk",
            "Adjustment Factor ID",
            "adjustment_factor-pk"
        ),
        adjustmentFactorName: defineProps(
            "adjustmentFactorName",
            "Adjustment Factor Name",
            "adjustment_factor-name"
        ),
        adjustmentFactorDescription: defineProps(
            "adjustmentFactorDescription",
            "Adjustment Factor Description",
            "adjustment_factor-description"
        ),
        /* eslint-enable */
    },
    ERv2Settings = {
        AXIS_OPTIONS: {
            studyShortCitation: defineAxis(ER.studyShortCitation),
            studyDesign: defineAxis(ER.studyDesign),
            designSource: defineAxis(ER.designSource),
            designCountries: defineAxis(ER.designCountries, {delimiter: "|"}),
            designAgeProfile: defineAxis(ER.designAgeProfile, {delimiter: "|"}),
            chemicalName: defineAxis(ER.chemicalName),
            exposureMeasurementType: defineAxis(ER.exposureMeasurementType, {delimiter: "|"}),
            exposureRoute: defineAxis(ER.exposureRoute),
            outcomeSystem: defineAxis(ER.outcomeSystem),
            outcomeEffect: defineAxis(ER.outcomeEffect),
            outcomeEndpoint: defineAxis(ER.outcomeEndpoint),
            outcomeSystemEffect: defineMultiAxis(
                [ER.outcomeSystem, ER.outcomeEffect],
                "outcomeSystemEffect",
                "Outcome System & Effect"
            ),
            outcomeSystemEndpoint: defineMultiAxis(
                [ER.outcomeSystem, ER.outcomeEndpoint],
                "outcomeSystemEndpoint",
                "Outcome System & Endpoint"
            ),
        },
        FILTER_OPTIONS: {
            studyShortCitation: defineFilter(ER.studyShortCitation, {on_click_event: "study"}),
            studyDesign: defineFilter(ER.studyDesign),
            designSource: defineFilter(ER.designSource),
            designCountries: defineFilter(ER.designCountries, {delimiter: "|"}),
            designAgeProfile: defineFilter(ER.designAgeProfile, {delimiter: "|"}),
            chemicalName: defineFilter(ER.chemicalName),
            exposureMeasurementType: defineFilter(ER.exposureMeasurementType, {delimiter: "|"}),
            exposureRoute: defineFilter(ER.exposureRoute),
            outcomeSystem: defineFilter(ER.outcomeSystem),
            outcomeEffect: defineFilter(ER.outcomeEffect),
            outcomeEndpoint: defineFilter(ER.outcomeEndpoint),
        },
        TABLE_FIELDS: {
            studyShortCitation: defineTable(ER.studyShortCitation, {on_click_event: "study"}),
            studyDesign: defineTable(ER.studyDesign),
            designSummary: defineTable(ER.designSummary),
            designSource: defineTable(ER.designSource),
            designCountries: defineTable(ER.designCountries, {delimiter: "|"}),
            designAgeProfile: defineTable(ER.designAgeProfile, {delimter: "|"}),
            designParticipantN: defineTable(ER.designParticipantN),
            chemicalName: defineTable(ER.chemicalName),
            exposureMeasurementType: defineTable(ER.exposureMeasurementType, {delimiter: "|"}),
            exposureRoute: defineTable(ER.exposureRoute),
            outcomeSystem: defineTable(ER.outcomeSystem),
            outcomeEffect: defineTable(ER.outcomeEffect),
            outcomeEndpoint: defineTable(ER.outcomeEndpoint),
            dataExtractionN: defineTable(ER.dataExtractionN),
            dataExtractionEffectEstimateType: defineTable(ER.dataExtractionEffectEstimateType),
            dataExtractionEffectEstimate: defineTable(ER.dataExtractionEffectEstimate),
        },
        DASHBOARDS: [],
    };
ERv2Settings.DASHBOARDS = [
    {
        id: "design-system-endpoint",
        label: "Design vs System & Endpoint",
        upperColor: COLORS.blue,
        x_axis: ERv2Settings.AXIS_OPTIONS.studyDesign.id,
        y_axis: ERv2Settings.AXIS_OPTIONS.outcomeSystemEndpoint.id,
        filters: [
            ERv2Settings.FILTER_OPTIONS.studyShortCitation.id,
            ERv2Settings.FILTER_OPTIONS.studyDesign.id,
            ERv2Settings.FILTER_OPTIONS.designCountries.id,
            ERv2Settings.FILTER_OPTIONS.chemicalName.id,
        ],
        table_fields: [
            ERv2Settings.TABLE_FIELDS.studyShortCitation.id,
            ERv2Settings.TABLE_FIELDS.studyDesign.id,
            ERv2Settings.TABLE_FIELDS.chemicalName.id,
            ERv2Settings.TABLE_FIELDS.exposureMeasurementType.id,
            ERv2Settings.TABLE_FIELDS.outcomeSystem.id,
            ERv2Settings.TABLE_FIELDS.outcomeEndpoint.id,
            ERv2Settings.TABLE_FIELDS.dataExtractionN.id,
            ERv2Settings.TABLE_FIELDS.dataExtractionEffectEstimateType.id,
            ERv2Settings.TABLE_FIELDS.dataExtractionEffectEstimate.id,
        ],
    },
    {
        id: "citation-vs-system",
        label: "Study vs System",
        upperColor: COLORS.green,
        x_axis: ERv2Settings.AXIS_OPTIONS.outcomeSystem.id,
        y_axis: ERv2Settings.AXIS_OPTIONS.studyShortCitation.id,
        filters: [
            ERv2Settings.FILTER_OPTIONS.studyDesign.id,
            ERv2Settings.FILTER_OPTIONS.exposureMeasurementType.id,
            ERv2Settings.FILTER_OPTIONS.chemicalName.id,
            ERv2Settings.FILTER_OPTIONS.outcomeEffect.id,
        ],
        table_fields: [
            ERv2Settings.TABLE_FIELDS.studyShortCitation.id,
            ERv2Settings.TABLE_FIELDS.studyDesign.id,
            ERv2Settings.TABLE_FIELDS.chemicalName.id,
            ERv2Settings.TABLE_FIELDS.exposureMeasurementType.id,
            ERv2Settings.TABLE_FIELDS.outcomeSystem.id,
            ERv2Settings.TABLE_FIELDS.outcomeEndpoint.id,
            ERv2Settings.TABLE_FIELDS.dataExtractionN.id,
            ERv2Settings.TABLE_FIELDS.dataExtractionEffectEstimateType.id,
            ERv2Settings.TABLE_FIELDS.dataExtractionEffectEstimate.id,
        ],
    },
];

export {ERv2Settings, ESDv2Settings};
