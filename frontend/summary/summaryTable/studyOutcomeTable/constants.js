import h from "shared/utils/helpers";

export const dataUrl = id => `/ani/api/assessment/${id}/endpoint-doses-heatmap/`,
    rowTypeChoices = [{id: "study", label: "Study"}],
    columnChoices = [
        {id: "rob_score", label: "rob_score"},
        {id: "study_name", label: "study_name"},
        {id: "species_strain_sex", label: "species_strain_sex"},
        {id: "doses", label: "doses"},
        {id: "free_html", label: "free_html"},
    ],
    createNewRow = studyId => {
        return {id: studyId, type: "study", customized: []};
    },
    createNewColumn = () => {
        return {label: "Study name", attribute: "study_name", key: h.randomString(5), width: 1};
    };
