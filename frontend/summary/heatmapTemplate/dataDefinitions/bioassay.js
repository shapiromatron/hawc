import {defineProps, defineAxis, defineMultiAxis, defineFilter, defineTable} from "./shared";

// BSD = bioassay study design
const BSD = {
        studyId: defineProps("studyId", "Study ID", "study id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study citation"),
        studyIdentifier: defineProps("studyIdentifier", "Study identifier", "study identifier"),
        experimentType: defineProps("experimentType", "Study design", "experiment type"),
        species: defineProps("species", "Species", "species"),
        strain: defineProps("strain", "Strain", "strain"),
        routeOfExposure: defineProps("routeOfExposure", "Route of exposure", "route of exposure"),
        experimentChemical: defineProps("experimentChemical", "Chemical", "experiment chemical"),
        sex: defineProps("sex", "Sex", "sex"),
        system: defineProps("system", "System", "system"),
        organ: defineProps("organ", "Organ", "organ"),
        effect: defineProps("effect", "Effect", "effect"),
        doseUnits: defineProps("doseUnits", "Dose units", "dose units"),
    },
    BSDSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(BSD.studyCitation),
            doseUnits: defineAxis(BSD.doseUnits, {delimiter: "|"}),
            experimentType: defineAxis(BSD.experimentType, {delimiter: "|"}),
            routeOfExposure: defineAxis(BSD.routeOfExposure, {delimiter: "|"}),
            experimentChemical: defineAxis(BSD.experimentChemical, {delimiter: "|"}),
            speciesSex: defineMultiAxis([BSD.species, BSD.sex], "speciesSex", "Species & sex", {
                delimiter: "|",
            }),
            speciesStrain: defineMultiAxis(
                [BSD.species, BSD.strain],
                "speciesStrain",
                "Species & strain",
                {delimiter: "|"}
            ),
            system: defineAxis(BSD.system, {delimiter: "|"}),
            organ: defineAxis(BSD.organ, {delimiter: "|"}),
            effect: defineAxis(BSD.effect, {delimiter: "|"}),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(BSD.studyCitation, {on_click_event: "study"}),
            studyIdentifier: defineFilter(BSD.studyIdentifier, {on_click_event: "study"}),
            experimentType: defineFilter(BSD.experimentType, {delimiter: "|"}),
            species: defineFilter(BSD.species, {delimiter: "|"}),
            strain: defineFilter(BSD.strain, {delimiter: "|"}),
            routeOfExposure: defineFilter(BSD.routeOfExposure, {delimiter: "|"}),
            experimentChemical: defineFilter(BSD.experimentChemical, {delimiter: "|"}),
            sex: defineFilter(BSD.sex, {delimiter: "|"}),
            system: defineFilter(BSD.system, {delimiter: "|"}),
            organ: defineFilter(BSD.organ, {delimiter: "|"}),
            effect: defineFilter(BSD.effect, {delimiter: "|"}),
            doseUnits: defineFilter(BSD.doseUnits, {delimiter: "|"}),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(BSD.studyCitation, {on_click_event: "study"}),
            studyIdentifier: defineTable(BSD.studyIdentifier, {on_click_event: "study"}),
            experimentType: defineTable(BSD.experimentType, {delimiter: "|"}),
            species: defineTable(BSD.species, {delimiter: "|"}),
            strain: defineTable(BSD.strain, {delimiter: "|"}),
            routeOfExposure: defineTable(BSD.routeOfExposure, {delimiter: "|"}),
            experimentChemical: defineTable(BSD.experimentChemical, {delimiter: "|"}),
            sex: defineTable(BSD.sex, {delimiter: "|"}),
            system: defineTable(BSD.system, {delimiter: "|"}),
            organ: defineTable(BSD.organ, {delimiter: "|"}),
            effect: defineTable(BSD.effect, {delimiter: "|"}),
            doseUnits: defineTable(BSD.doseUnits, {delimiter: "|"}),
        },
        DASHBOARDS: [],
    };

// define dashboards after building-blocks are defined
BSDSettings.DASHBOARDS = [
    {
        id: "study design vs. system",
        label: "study design vs. system",
        x_axis: BSDSettings.AXIS_OPTIONS.experimentType.id,
        y_axis: BSDSettings.AXIS_OPTIONS.system.id,
        filters: [
            BSDSettings.FILTER_OPTIONS.studyCitation.id,
            BSDSettings.FILTER_OPTIONS.routeOfExposure.id,
            BSDSettings.FILTER_OPTIONS.experimentChemical.id,
        ],
        table_fields: [
            BSDSettings.TABLE_FIELDS.studyCitation.id,
            BSDSettings.TABLE_FIELDS.species.id,
            BSDSettings.TABLE_FIELDS.sex.id,
            BSDSettings.TABLE_FIELDS.system.id,
            BSDSettings.TABLE_FIELDS.organ.id,
            BSDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "test subject vs. system",
        label: "test subject vs. system",
        x_axis: BSDSettings.AXIS_OPTIONS.speciesSex.id,
        y_axis: BSDSettings.AXIS_OPTIONS.system.id,
        filters: [
            BSDSettings.FILTER_OPTIONS.studyCitation.id,
            BSDSettings.FILTER_OPTIONS.experimentType.id,
            BSDSettings.FILTER_OPTIONS.experimentChemical.id,
        ],
        table_fields: [
            BSDSettings.TABLE_FIELDS.studyCitation.id,
            BSDSettings.TABLE_FIELDS.experimentType.id,
            BSDSettings.TABLE_FIELDS.routeOfExposure.id,
            BSDSettings.TABLE_FIELDS.experimentChemical.id,
            BSDSettings.TABLE_FIELDS.system.id,
            BSDSettings.TABLE_FIELDS.organ.id,
            BSDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "system vs. study citation",
        label: "system vs. study citation",
        x_axis: BSDSettings.AXIS_OPTIONS.system.id,
        y_axis: BSDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [],
        table_fields: [
            BSDSettings.TABLE_FIELDS.studyCitation.id,
            BSDSettings.TABLE_FIELDS.experimentType.id,
            BSDSettings.TABLE_FIELDS.species.id,
            BSDSettings.TABLE_FIELDS.strain.id,
            BSDSettings.TABLE_FIELDS.sex.id,
            BSDSettings.TABLE_FIELDS.routeOfExposure.id,
            BSDSettings.TABLE_FIELDS.experimentChemical.id,
            BSDSettings.TABLE_FIELDS.system.id,
            BSDSettings.TABLE_FIELDS.organ.id,
            BSDSettings.TABLE_FIELDS.effect.id,
        ],
    },
    {
        id: "dose units vs. study citation",
        label: "dose units vs. study citation",
        x_axis: BSDSettings.AXIS_OPTIONS.doseUnits.id,
        y_axis: BSDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            BSDSettings.FILTER_OPTIONS.experimentType.id,
            BSDSettings.FILTER_OPTIONS.routeOfExposure.id,
            BSDSettings.FILTER_OPTIONS.experimentChemical.id,
        ],
        table_fields: [
            BSDSettings.TABLE_FIELDS.studyCitation.id,
            BSDSettings.TABLE_FIELDS.species.id,
            BSDSettings.TABLE_FIELDS.sex.id,
            BSDSettings.TABLE_FIELDS.system.id,
            BSDSettings.TABLE_FIELDS.organ.id,
            BSDSettings.TABLE_FIELDS.effect.id,
            BSDSettings.TABLE_FIELDS.doseUnits.id,
        ],
    },

    {
        id: "chemical vs. study citation",
        label: "chemical vs. study citation",
        x_axis: BSDSettings.AXIS_OPTIONS.experimentChemical.id,
        y_axis: BSDSettings.AXIS_OPTIONS.studyCitation.id,
        filters: [
            BSDSettings.FILTER_OPTIONS.experimentType.id,
            BSDSettings.FILTER_OPTIONS.routeOfExposure.id,
            BSDSettings.FILTER_OPTIONS.system.id,
        ],
        table_fields: [
            BSDSettings.TABLE_FIELDS.studyCitation.id,
            BSDSettings.TABLE_FIELDS.species.id,
            BSDSettings.TABLE_FIELDS.sex.id,
            BSDSettings.TABLE_FIELDS.system.id,
            BSDSettings.TABLE_FIELDS.organ.id,
            BSDSettings.TABLE_FIELDS.effect.id,
        ],
    },
];

// BE = Bioassay endpoints
const BE = {
        endpointId: defineProps("endpointId", "Endpoint ID", "endpoint id"),
        endpointName: defineProps("endpointName", "Endpoint name", "endpoint name"),
        system: defineProps("system", "System", "system"),
        organ: defineProps("organ", "Organ", "organ"),
        effect: defineProps("effect", "Effect", "effect"),
        effectSubtype: defineProps("effectSubtype", "Effect subtype", "effect subtype"),
        routeOfExposure: defineProps("routeOfExposure", "Route of exposure", "route of exposure"),
        species: defineProps("species", "Species", "species"),
        strain: defineProps("strain", "Strain", "strain"),
        animalGroupName: defineProps("animalGroupName", "Animal group name", "animal group name"),
        sex: defineProps("sex", "Sex", "sex"),
        generation: defineProps("generation", "Generation", "generation"),
        animalGroupId: defineProps("animalGroupId", "Animal group id", "animal group id"),
        experimentId: defineProps("experimentId", "Experiment id", "experiment id"),
        experimentName: defineProps("experimentName", "Experiment name", "experiment name"),
        experimentType: defineProps("experimentType", "Study design", "experiment type"),
        experimentCas: defineProps("experimentCas", "Experiment CAS", "experiment cas"),
        experimentChemical: defineProps(
            "experimentChemical",
            "Experiment chemical",
            "experiment chemical"
        ),
        studyId: defineProps("studyId", "Study id", "study id"),
        studyCitation: defineProps("studyCitation", "Study citation", "study citation"),
        studyIdentifier: defineProps("studyIdentifier", "Study identifier", "study identifier"),
    },
    BESettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(BE.studyCitation),
            speciesSex: defineMultiAxis([BE.species, BE.sex], "speciesSex", "Species & Sex"),
            experimentType: defineAxis(BE.experimentType),
            system: defineAxis(BE.system),
            organ: defineAxis(BE.organ),
            systemOrgan: defineMultiAxis([BE.system, BE.organ], "systemOrgan", "System & organ"),
            experimentTypeSystem: defineMultiAxis(
                [BE.experimentType, BE.system],
                "experimentTypeSystem",
                "Study design & system"
            ),
            endpointName: defineAxis(BE.endpointName),
        },
        FILTER_OPTIONS: {
            studyCitation: defineFilter(BE.studyCitation, {on_click_event: "study"}),
            experimentType: defineFilter(BE.experimentType),
            species: defineFilter(BE.species),
            strain: defineFilter(BE.strain),
            sex: defineFilter(BE.sex),
            system: defineFilter(BE.system),
            organ: defineFilter(BE.organ),
            effect: defineFilter(BE.effect),
            effectSubtype: defineFilter(BE.effectSubtype),
            endpointName: defineFilter(BE.endpointName),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(BE.studyCitation, {on_click_event: "study"}),
            experimentName: defineTable(BE.experimentName, {on_click_event: "experiment"}),
            animalGroupName: defineTable(BE.animalGroupName, {on_click_event: "animal_group"}),
            species: defineTable(BE.species),
            strain: defineTable(BE.strain),
            sex: defineTable(BE.sex),
            system: defineTable(BE.system),
            organ: defineTable(BE.organ),
            effect: defineTable(BE.effect),
            effectSubtype: defineTable(BE.effectSubtype),
            endpointName: defineTable(BE.endpointName, {on_click_event: "endpoint_complete"}),
        },
        DASHBOARDS: [],
    };

// define dashboards after building-blocks are defined
BESettings.DASHBOARDS = [
    {
        id: "system-vs-test-subject",
        label: "system vs. test subject",
        x_axis: BESettings.AXIS_OPTIONS.speciesSex.id,
        y_axis: BESettings.AXIS_OPTIONS.system.id,
        filters: [
            BESettings.FILTER_OPTIONS.experimentType.id,
            BESettings.FILTER_OPTIONS.studyCitation.id,
            BESettings.FILTER_OPTIONS.effect.id,
        ],
        table_fields: [
            BESettings.TABLE_FIELDS.studyCitation.id,
            BESettings.TABLE_FIELDS.experimentName.id,
            BESettings.TABLE_FIELDS.animalGroupName.id,
            BESettings.TABLE_FIELDS.system.id,
            BESettings.TABLE_FIELDS.organ.id,
            BESettings.TABLE_FIELDS.effect.id,
            BESettings.TABLE_FIELDS.endpointName.id,
        ],
    },
    {
        id: "test-subject-vs-study-design-system",
        label: "test subjects vs. study design & system",
        x_axis: BESettings.AXIS_OPTIONS.speciesSex.id,
        y_axis: BESettings.AXIS_OPTIONS.experimentTypeSystem.id,
        filters: [
            BESettings.FILTER_OPTIONS.experimentType.id,
            BESettings.FILTER_OPTIONS.organ.id,
            BESettings.FILTER_OPTIONS.effect.id,
        ],
        table_fields: [
            BESettings.TABLE_FIELDS.studyCitation.id,
            BESettings.TABLE_FIELDS.experimentName.id,
            BESettings.TABLE_FIELDS.animalGroupName.id,
            BESettings.TABLE_FIELDS.system.id,
            BESettings.TABLE_FIELDS.organ.id,
            BESettings.TABLE_FIELDS.effect.id,
            BESettings.TABLE_FIELDS.endpointName.id,
        ],
    },
    {
        id: "reference-vs-system",
        label: "reference vs. system",
        x_axis: BESettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: BESettings.AXIS_OPTIONS.system.id,
        filters: [],
        table_fields: [
            BESettings.TABLE_FIELDS.studyCitation.id,
            BESettings.TABLE_FIELDS.experimentName.id,
            BESettings.TABLE_FIELDS.animalGroupName.id,
            BESettings.TABLE_FIELDS.system.id,
            BESettings.TABLE_FIELDS.organ.id,
            BESettings.TABLE_FIELDS.effect.id,
            BESettings.TABLE_FIELDS.endpointName.id,
        ],
    },
    {
        id: "reference-vs-study-design-system",
        label: "reference vs. study design & system",
        x_axis: BESettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: BESettings.AXIS_OPTIONS.experimentTypeSystem.id,
        filters: [],
        table_fields: [
            BESettings.TABLE_FIELDS.studyCitation.id,
            BESettings.TABLE_FIELDS.experimentName.id,
            BESettings.TABLE_FIELDS.animalGroupName.id,
            BESettings.TABLE_FIELDS.system.id,
            BESettings.TABLE_FIELDS.organ.id,
            BESettings.TABLE_FIELDS.effect.id,
            BESettings.TABLE_FIELDS.endpointName.id,
        ],
    },
];

// BED = Bioassay endpoint doses
const BED = {
        endpointId: defineProps("endpointId", "endpoint id", "endpoint id"),
        endpointName: defineProps("endpointName", "endpoint name", "endpoint name"),
        system: defineProps("system", "system", "system"),
        organ: defineProps("organ", "organ", "organ"),
        effect: defineProps("effect", "effect", "effect"),
        effectSubtype: defineProps("effectSubtype", "effect subtype", "effect subtype"),
        routeOfExposure: defineProps("routeOfExposure", "route of exposure", "route of exposure"),
        species: defineProps("species", "species", "species"),
        strain: defineProps("strain", "strain", "strain"),
        animalGroupName: defineProps("animalGroupName", "animal group name", "animal group name"),
        sex: defineProps("sex", "sex", "sex"),
        generation: defineProps("generation", "generation", "generation"),
        animalGroupId: defineProps("animalGroupId", "animal group id", "animal group id"),
        experimentId: defineProps("experimentId", "experiment id", "experiment id"),
        experimentName: defineProps("experimentName", "experiment name", "experiment name"),
        experimentType: defineProps("experimentType", "experiment type", "experiment type"),
        experimentCas: defineProps("experimentCas", "experiment cas", "experiment cas"),
        experimentChemical: defineProps(
            "experimentChemical",
            "experiment chemical",
            "experiment chemical"
        ),
        studyId: defineProps("studyId", "study id", "study id"),
        studyCitation: defineProps("studyCitation", "study citation", "study citation"),
        studyIdentifier: defineProps("studyIdentifier", "study identifier", "study identifier"),
        doseUnitsId: defineProps("doseUnitsId", "dose units id", "dose units id"),
        doseUnitsName: defineProps("doseUnitsName", "dose units name", "dose units name"),
        doses: defineProps("doses", "doses", "doses"),
        noel: defineProps("noel", "noel", "noel"),
        loel: defineProps("loel", "loel", "loel"),
        fel: defineProps("fel", "fel", "fel"),
        bmd: defineProps("bmd", "bmd", "bmd"),
        bmdl: defineProps("bmdl", "bmdl", "bmdl"),
    },
    BEDSettings = {
        AXIS_OPTIONS: {
            studyCitation: defineAxis(BED.studyCitation),
            speciesSex: defineMultiAxis([BED.species, BED.sex], "speciesSex", "Species & Sex"),
            experimentType: defineAxis(BED.experimentType),
            system: defineAxis(BED.system),
            organ: defineAxis(BED.organ),
            systemOrgan: defineMultiAxis([BED.system, BED.organ], "systemOrgan", "System & organ"),
            experimentTypeSystem: defineMultiAxis(
                [BED.experimentType, BED.system],
                "experimentTypeSystem",
                "Study design & system"
            ),
            endpointName: defineAxis(BED.endpointName),
        },
        FILTER_OPTIONS: {
            doseUnitsName: defineFilter(BED.doseUnitsName),
            studyCitation: defineFilter(BED.studyCitation, {on_click_event: "study"}),
            experimentType: defineFilter(BED.experimentType),
            species: defineFilter(BED.species),
            strain: defineFilter(BED.strain),
            sex: defineFilter(BED.sex),
            system: defineFilter(BED.system),
            organ: defineFilter(BED.organ),
            effect: defineFilter(BED.effect, {on_click_event: "endpoint_complete"}),
            effectSubtype: defineFilter(BED.effectSubtype, {on_click_event: "endpoint_complete"}),
            endpointName: defineFilter(BED.endpointName),
        },
        TABLE_FIELDS: {
            studyCitation: defineTable(BED.studyCitation, {on_click_event: "study"}),
            experimentName: defineTable(BED.experimentName, {on_click_event: "experiment"}),
            animalGroupName: defineTable(BED.animalGroupName, {on_click_event: "animal_group"}),
            species: defineTable(BED.species),
            strain: defineTable(BED.strain),
            sex: defineTable(BED.sex),
            system: defineTable(BED.system),
            organ: defineTable(BED.organ),
            effect: defineTable(BED.effect),
            effectSubtype: defineTable(BED.effectSubtype),
            endpointName: defineTable(BED.endpointName, {on_click_event: "endpoint_complete"}),
            doses: defineTable(BED.doses),
            doseUnitsName: defineTable(BED.doseUnitsName),
            noel: defineTable(BED.noel),
            loel: defineTable(BED.loel),
            fel: defineTable(BED.fel),
            bmd: defineTable(BED.bmd),
            bmdl: defineTable(BED.bmdl),
        },
        DASHBOARDS: [],
    };

// define dashboards after building-blocks are defined
BEDSettings.DASHBOARDS = [
    {
        id: "system-vs-test-subject",
        label: "system vs. test subject",
        x_axis: BEDSettings.AXIS_OPTIONS.experimentType.id,
        y_axis: BEDSettings.AXIS_OPTIONS.system.id,
        filters: [
            BEDSettings.FILTER_OPTIONS.doseUnitsName.id,
            BEDSettings.FILTER_OPTIONS.experimentType.id,
            BEDSettings.FILTER_OPTIONS.studyCitation.id,
            BEDSettings.FILTER_OPTIONS.effect.id,
        ],
        table_fields: [
            BEDSettings.TABLE_FIELDS.studyCitation.id,
            BEDSettings.TABLE_FIELDS.experimentName.id,
            BEDSettings.TABLE_FIELDS.animalGroupName.id,
            BEDSettings.TABLE_FIELDS.system.id,
            BEDSettings.TABLE_FIELDS.organ.id,
            BEDSettings.TABLE_FIELDS.effect.id,
            BEDSettings.TABLE_FIELDS.endpointName.id,
            BEDSettings.TABLE_FIELDS.doses.id,
            BEDSettings.TABLE_FIELDS.doseUnitsName.id,
            BEDSettings.TABLE_FIELDS.noel.id,
            BEDSettings.TABLE_FIELDS.loel.id,
            BEDSettings.TABLE_FIELDS.bmd.id,
            BEDSettings.TABLE_FIELDS.bmdl.id,
        ],
    },
    {
        id: "test-subject-vs-study-design-system",
        label: "test subjects vs. study design & system",
        x_axis: BEDSettings.AXIS_OPTIONS.speciesSex.id,
        y_axis: BEDSettings.AXIS_OPTIONS.experimentTypeSystem.id,
        filters: [
            BEDSettings.FILTER_OPTIONS.doseUnitsName.id,
            BEDSettings.FILTER_OPTIONS.studyCitation.id,
            BEDSettings.FILTER_OPTIONS.organ.id,
            BEDSettings.FILTER_OPTIONS.effect.id,
        ],
        table_fields: [
            BEDSettings.TABLE_FIELDS.studyCitation.id,
            BEDSettings.TABLE_FIELDS.experimentName.id,
            BEDSettings.TABLE_FIELDS.animalGroupName.id,
            BEDSettings.TABLE_FIELDS.system.id,
            BEDSettings.TABLE_FIELDS.organ.id,
            BEDSettings.TABLE_FIELDS.effect.id,
            BEDSettings.TABLE_FIELDS.endpointName.id,
            BEDSettings.TABLE_FIELDS.doses.id,
            BEDSettings.TABLE_FIELDS.doseUnitsName.id,
            BEDSettings.TABLE_FIELDS.noel.id,
            BEDSettings.TABLE_FIELDS.loel.id,
            BEDSettings.TABLE_FIELDS.bmd.id,
            BEDSettings.TABLE_FIELDS.bmdl.id,
        ],
    },
    {
        id: "reference-vs-system",
        label: "reference vs. system",
        x_axis: BEDSettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: BEDSettings.AXIS_OPTIONS.system.id,
        filters: [BEDSettings.FILTER_OPTIONS.doseUnitsName.id],
        table_fields: [
            BEDSettings.TABLE_FIELDS.studyCitation.id,
            BEDSettings.TABLE_FIELDS.experimentName.id,
            BEDSettings.TABLE_FIELDS.animalGroupName.id,
            BEDSettings.TABLE_FIELDS.system.id,
            BEDSettings.TABLE_FIELDS.organ.id,
            BEDSettings.TABLE_FIELDS.effect.id,
            BEDSettings.TABLE_FIELDS.endpointName.id,
            BEDSettings.TABLE_FIELDS.doses.id,
            BEDSettings.TABLE_FIELDS.doseUnitsName.id,
            BEDSettings.TABLE_FIELDS.noel.id,
            BEDSettings.TABLE_FIELDS.loel.id,
            BEDSettings.TABLE_FIELDS.bmd.id,
            BEDSettings.TABLE_FIELDS.bmdl.id,
        ],
    },
    {
        id: "reference-vs-study-design-system",
        label: "reference vs. study design & system",
        x_axis: BEDSettings.AXIS_OPTIONS.studyCitation.id,
        y_axis: BEDSettings.AXIS_OPTIONS.experimentTypeSystem.id,
        filters: [BEDSettings.FILTER_OPTIONS.doseUnitsName.id],
        table_fields: [
            BEDSettings.TABLE_FIELDS.studyCitation.id,
            BEDSettings.TABLE_FIELDS.experimentName.id,
            BEDSettings.TABLE_FIELDS.animalGroupName.id,
            BEDSettings.TABLE_FIELDS.system.id,
            BEDSettings.TABLE_FIELDS.organ.id,
            BEDSettings.TABLE_FIELDS.effect.id,
            BEDSettings.TABLE_FIELDS.endpointName.id,
            BEDSettings.TABLE_FIELDS.doses.id,
            BEDSettings.TABLE_FIELDS.doseUnitsName.id,
            BEDSettings.TABLE_FIELDS.noel.id,
            BEDSettings.TABLE_FIELDS.loel.id,
            BEDSettings.TABLE_FIELDS.bmd.id,
            BEDSettings.TABLE_FIELDS.bmdl.id,
        ],
    },
];

export {BSDSettings, BESettings, BEDSettings};
