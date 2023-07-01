import {COLORS, defineAxis, defineFilter, defineProps, defineTable} from "./shared";

// ESD = epi study design
const ESD = {
        study_id: defineProps("study_id", "Study ID", "id"),
        PMID: defineProps("PMID", "PubMed ID", "PMID"),
        HERO: defineProps("HERO", "HERO ID", "HERO"),
        DOI: defineProps("DOI", "DOI", "DOI"),
        short_citation: defineProps("short_citation", "Study citation", "short_citation"),
        full_citation: defineProps("full_citation", "Full Citation", "full_citation"),
        coi_reported: defineProps("coi_reported", "COI Reported", "coi_reported"),
        coi_details: defineProps("coi_details", "COI Details", "coi_details"),
        funding_source: defineProps("funding_source", "Funding Source", "funding_source"),
        study_identifier: defineProps("study_identifier", "Study Identifier", "study_identifier"),
        contact_author: defineProps("contact_author", "Author Contacted", "contact_author"),
        ask_author: defineProps("ask_author", "Author Notes", "ask_author"),
        published: defineProps("published", "Published", "published"),
        summary: defineProps("summary", "Summary", "summary"),
        study_design: defineProps("study_design", "Study Design", "study_design"),
        countries: defineProps("countries", "Countries", "countries"),
        design_source: defineProps("design_source", "Design Source", "design_source"),
        age_profile: defineProps("age_profile", "Age Profile", "age_profile"),
        chemical_name: defineProps("chemical_name", "Chemical Name", "chemical_name"),
        exposure_name: defineProps("exposure_name", "Exposure Name", "exposure_name"),
        outcome_systems: defineProps("outcome_systems", "Systems", "outcome_systems"),
        outcome_effects: defineProps("outcome_effects", "Effects", "outcome_effects"),
        outcome_endpoints: defineProps("outcome_endpoints", "Endpoints", "outcome_endpoints"),
    },
    ESDv2Settings = {
        AXIS_OPTIONS: {
            short_citation: defineAxis(ESD.short_citation),
            countries: defineAxis(ESD.countries, {delimiter: "|"}),
            design_source: defineAxis(ESD.design_source, {delimiter: "|"}),
            age_profile: defineAxis(ESD.age_profile, {delimiter: "|"}),
            chemical_name: defineAxis(ESD.chemical_name, {delimiter: "|"}),
            exposure_name: defineAxis(ESD.exposure_name, {delimiter: "|"}),
            outcome_systems: defineAxis(ESD.outcome_systems, {delimiter: "|"}),
            outcome_effects: defineAxis(ESD.outcome_effects, {delimiter: "|"}),
            outcome_endpoints: defineAxis(ESD.outcome_endpoints, {delimiter: "|"}),
        },
        FILTER_OPTIONS: {
            short_citation: defineFilter(ESD.short_citation, {on_click_event: "study"}),
            countries: defineFilter(ESD.countries, {delimiter: "|"}),
            design_source: defineFilter(ESD.design_source, {delimiter: "|"}),
            age_profile: defineFilter(ESD.age_profile, {delimiter: "|"}),
            chemical_name: defineFilter(ESD.chemical_name, {delimiter: "|"}),
            exposure_name: defineFilter(ESD.exposure_name, {delimiter: "|"}),
            outcome_systems: defineFilter(ESD.outcome_systems, {delimiter: "|"}),
            outcome_effects: defineFilter(ESD.outcome_effects, {delimiter: "|"}),
            outcome_endpoints: defineFilter(ESD.outcome_endpoints, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            short_citation: defineTable(ESD.short_citation, {on_click_event: "study"}),
            full_citation: defineTable(ESD.full_citation),
            countries: defineTable(ESD.countries, {delimiter: "|"}),
            design_source: defineTable(ESD.design_source, {delimiter: "|"}),
            age_profile: defineTable(ESD.age_profile, {delimiter: "|"}),
            chemical_name: defineTable(ESD.chemical_name, {delimiter: "|"}),
            exposure_name: defineTable(ESD.exposure_name, {delimiter: "|"}),
            outcome_systems: defineTable(ESD.outcome_systems, {delimiter: "|"}),
            outcome_effects: defineTable(ESD.outcome_effects, {delimiter: "|"}),
            outcome_endpoints: defineTable(ESD.outcome_endpoints, {delimiter: "|"}),
        },
    };
ESDv2Settings.DASHBOARDS = [
    {
        id: "study_v_design",
        label: "Study by design",
        upperColor: COLORS.green,
        x_axis: ESDv2Settings.AXIS_OPTIONS.design_source.id,
        y_axis: ESDv2Settings.AXIS_OPTIONS.short_citation.id,
        filters: [
            ESDv2Settings.FILTER_OPTIONS.short_citation.id,
            ESDv2Settings.FILTER_OPTIONS.countries.id,
            ESDv2Settings.FILTER_OPTIONS.design_source.id,
            ESDv2Settings.FILTER_OPTIONS.age_profile.id,
            ESDv2Settings.FILTER_OPTIONS.chemical_name.id,
            ESDv2Settings.FILTER_OPTIONS.exposure_name.id,
            ESDv2Settings.FILTER_OPTIONS.outcome_systems.id,
            ESDv2Settings.FILTER_OPTIONS.outcome_effects.id,
            ESDv2Settings.FILTER_OPTIONS.outcome_endpoints.id,
        ],
        table_fields: [
            ESDv2Settings.TABLE_FIELDS.short_citation.id,
            ESDv2Settings.TABLE_FIELDS.full_citation.id,
            ESDv2Settings.TABLE_FIELDS.countries.id,
            ESDv2Settings.TABLE_FIELDS.design_source.id,
            ESDv2Settings.TABLE_FIELDS.age_profile.id,
            ESDv2Settings.TABLE_FIELDS.chemical_name.id,
            ESDv2Settings.TABLE_FIELDS.exposure_name.id,
            ESDv2Settings.TABLE_FIELDS.outcome_systems.id,
            ESDv2Settings.TABLE_FIELDS.outcome_effects.id,
            ESDv2Settings.TABLE_FIELDS.outcome_endpoints.id,
        ],
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
        x_axis: ERv2Settings.AXIS_OPTIONS.studyCitation.id,
        y_axis: ERv2Settings.AXIS_OPTIONS.studyCitation.id,
        filters: [ERv2Settings.FILTER_OPTIONS.studyCitation.id],
        table_fields: [ERv2Settings.TABLE_FIELDS.studyCitation.id],
    },
];

export {ERv2Settings, ESDv2Settings};
