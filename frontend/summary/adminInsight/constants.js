import _ from "lodash";

export const selectedModelChoices = [
    {id: 1, value: "User growth", url: "/assessment/api/dashboard/user_growth/"},
    {id: 2, value: "Assessment growth", url: "/assessment/api/dashboard/assessment_growth/"},
    {id: 3, value: "Study growth", url: "/assessment/api/dashboard/study_growth/"},
];

export const selectedModelChoiceMap = _.keyBy(selectedModelChoices, "id");
