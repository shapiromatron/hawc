import h from "shared/utils/helpers";

export const NM = {backgroundColor: "#DFDFDF", color: "#404040", html: "NM"},
    dataUrl = (table_type, data_source, assessment_id, published_only) =>
        `/summary/api/summary-table/data/?table_type=${table_type}&data_source=${data_source}&assessment_id=${assessment_id}&published_only=${published_only}`,
    robUrl = assessment_id => `/rob/api/assessment/${assessment_id}/settings/`,
    dataSourceChoices = [
        {id: "study", label: "Study evaluation"},
        {id: "ani", label: "Study evaluation + animal bioassay"},
    ],
    rowTypeChoices = {study: [{id: "study", label: "Study"}], ani: [{id: "study", label: "Study"}]},
    colAttributeChoices = {
        study: [
            {id: "free_html", label: "Free HTML"},
            {id: "study_name", label: "Study citation"},
            {id: "rob_score", label: "Evaluation"},
        ],
        ani: [
            {id: "free_html", label: "Free HTML"},
            {id: "study_name", label: "Study citation"},
            {id: "species_strain_sex", label: "Animal description"},
            {id: "doses", label: "Doses"},
            {id: "rob_score", label: "Evaluation"},
        ],
    },
    createNewRow = studyId => {
        return {id: studyId, type: "study", customized: []};
    },
    createNewColumn = () => {
        return {
            label: "Study citation",
            attribute: "study_name",
            key: h.randomString(5),
            width: 1,
        };
    },
    createNewSubheader = start => {
        return {label: "Label", start, length: 1};
    };
