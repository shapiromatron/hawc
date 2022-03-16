import h from "shared/utils/helpers";

export const NM = {backgroundColor: "#DFDFDF", color: "#404040", html: "NM"},
    dataUrl = (table_type, data_source, assessment_id, published_only) =>
        `/summary/api/summary-table/data/?table_type=${table_type}&data_source=${data_source}&assessment_id=${assessment_id}&published_only=${published_only}`,
    robUrl = assessment_id => `/rob/api/assessment/${assessment_id}/settings/`,
    DATA_SOURCE = {
        STUDY: {id: "study", label: "Study evaluation"},
        ANI: {id: "ani", label: "Study evaluation + bioassay"},
    },
    ROW_TYPE = {
        STUDY: {id: "study", label: "Study"},
        EXPERIMENT: {id: "experiment", label: "Experiment"},
        ANIMAL_GROUP: {id: "animal_group", label: "Animal group"},
    },
    COL_ATTRIBUTE = {
        STUDY_SHORT_CITATION: {id: "study_short_citation", label: "Study citation"},
        ROB: {id: "rob", label: "Study evaluation"},
        FREE_HTML: {id: "free_html", label: "Free text"},
        ANIMAL_GROUP_DESCRIPTION: {id: "animal_group_description", label: "Animal description"},
        ANIMAL_GROUP_DOSES: {id: "animal_group_doses", label: "Doses"},
        EXPERIMENT_NAME: {id: "experiment_name", label: "Experiment name"},
        ANIMAL_GROUP_NAME: {id: "animal_group_name", label: "Animal group name"},
        ANIMAL_GROUP_TREATMENT_PERIOD: {
            id: "animal_group_treatment_period",
            label: "Treatment period",
        },
        ANIMAL_GROUP_ROUTE_OF_EXPOSURE: {
            id: "animal_group_route_of_exposure",
            label: "Route of exposure",
        },
        ENDPOINT_SYSTEM: {id: "endpoint_system", label: "System"},
        ENDPOINT_EFFECT: {id: "endpoint_effect", label: "Effect"},
        ENDPOINT_NAME: {id: "endpoint_name", label: "Endpoint name"},
        EXPERIMENT_CHEMICAL: {id: "experiment_chemical", label: "Chemical"},
    },
    dataSourceChoices = [DATA_SOURCE.STUDY, DATA_SOURCE.ANI],
    rowTypeChoices = {
        [DATA_SOURCE.STUDY.id]: [ROW_TYPE.STUDY],
        [DATA_SOURCE.ANI.id]: [ROW_TYPE.STUDY, ROW_TYPE.EXPERIMENT, ROW_TYPE.ANIMAL_GROUP],
    },
    colAttributeChoices = {
        [DATA_SOURCE.STUDY.id]: [
            COL_ATTRIBUTE.STUDY_SHORT_CITATION,
            COL_ATTRIBUTE.ROB,
            COL_ATTRIBUTE.FREE_HTML,
        ],
        [DATA_SOURCE.ANI.id]: [
            COL_ATTRIBUTE.STUDY_SHORT_CITATION,
            COL_ATTRIBUTE.ANIMAL_GROUP_DESCRIPTION,
            COL_ATTRIBUTE.ANIMAL_GROUP_DOSES,
            COL_ATTRIBUTE.EXPERIMENT_NAME,
            COL_ATTRIBUTE.ANIMAL_GROUP_NAME,
            COL_ATTRIBUTE.ANIMAL_GROUP_TREATMENT_PERIOD,
            COL_ATTRIBUTE.ANIMAL_GROUP_ROUTE_OF_EXPOSURE,
            COL_ATTRIBUTE.ENDPOINT_SYSTEM,
            COL_ATTRIBUTE.ENDPOINT_EFFECT,
            COL_ATTRIBUTE.ENDPOINT_NAME,
            COL_ATTRIBUTE.EXPERIMENT_CHEMICAL,
            COL_ATTRIBUTE.ROB,
            COL_ATTRIBUTE.FREE_HTML,
        ],
    },
    createNewRow = studyId => {
        return {id: studyId, type: ROW_TYPE.STUDY.id, customized: []};
    },
    createNewColumn = () => {
        return {
            label: COL_ATTRIBUTE.STUDY_SHORT_CITATION.label,
            attribute: COL_ATTRIBUTE.STUDY_SHORT_CITATION.id,
            key: h.randomString(5),
            width: 1,
        };
    },
    createNewSubheader = start => {
        return {label: "Label", start, length: 1};
    };
