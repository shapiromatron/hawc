import _ from "lodash";

export const selectedModelChoices = [
    {id: 1, value: "User growth", model: "user"},
    {id: 2, value: "Assessment growth", model: "assessment"},
    {id: 3, value: "Study growth", model: "study"},
];

export const selectedModelChoiceMap = _.keyBy(selectedModelChoices, "id");
