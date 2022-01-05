import h from "shared/utils/helpers";

export const NM = {color: "#DFDFDF", html: "NM"},
    dataUrl = (table_type, data_source, assessment_id) =>
        `/summary/api/summary-table/data/?table_type=${table_type}&data_source=${data_source}&assessment_id=${assessment_id}`,
    robUrl = assessment_id => `/rob/api/assessment/${assessment_id}/settings/`,
    dataSourceChoices = [{id: "ani", label: "Animal bioassay"}],
    rowTypeChoices = [{id: "study", label: "Study"}],
    robAttributeChoices = [
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
        return {
            label: "Study name",
            attribute: "study_name",
            key: h.randomString(5),
            width: 1,
        };
    };
