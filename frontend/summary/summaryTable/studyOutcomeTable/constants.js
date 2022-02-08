import h from "shared/utils/helpers";

export const NM = {backgroundColor: "#DFDFDF", color: "#404040", html: "NM"},
    dataUrl = (table_type, data_source, assessment_id) =>
        `/summary/api/summary-table/data/?table_type=${table_type}&data_source=${data_source}&assessment_id=${assessment_id}`,
    robUrl = assessment_id => `/rob/api/assessment/${assessment_id}/settings/`,
    dataSourceChoices = [
        {id: "study", label: "Study evaluation (published only)"},
        {id: "ani", label: "Study evaluation + animal bioassay (published only)"},
    ],
    rowTypeChoices = {study: [{id: "study", label: "Study"}], ani: [{id: "study", label: "Study"}]},
    colAttributeChoices = {
        study: [
            {id: "rob_score", label: "rob_score"},
            {id: "study_name", label: "study_name"},
            {id: "free_html", label: "free_html"},
        ],
        ani: [
            {id: "rob_score", label: "rob_score"},
            {id: "study_name", label: "study_name"},
            {id: "species_strain_sex", label: "species_strain_sex"},
            {id: "doses", label: "doses"},
            {id: "free_html", label: "free_html"},
        ],
    },
    createNewRow = studyId => {
        return {id: studyId, type: "study", customized: []};
    },
    createNewColumn = () => {
        return {
            label: "Study name",
            attribute: "study_name",
            key: h.randomString(5),
            width: 1,
        };
    },
    createNewSubheader = start => {
        return {label: "Label", start, length: 1};
    };
