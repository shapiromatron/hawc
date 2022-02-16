import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import SelectInput from "shared/components/SelectInput";

import {NO_JUDGMENT, CUSTOM_JUDGMENT} from "./common";

const judgmentChoices = [
        {value: 30, icon: "⊕⊕⊕", text: "Robust"},
        {value: 20, icon: "⊕⊕⊙", text: "Moderate"},
        {value: 10, icon: "⊕⊙⊙", text: "Slight"},
        {value: 1, icon: "⊙⊙⊙", text: "Indeterminate"},
        {value: -10, icon: "⊝⊝⊝", text: "Evidence of no effect"},
        {value: NO_JUDGMENT, icon: "", text: "None"},
        {value: CUSTOM_JUDGMENT, icon: "", text: "Custom"},
    ],
    summaryJudgmentChoices = [
        {value: 30, icon: "⊕⊕⊕", text: "Evidence demonstrates"},
        {value: 20, icon: "⊕⊕⊙", text: "Evidence indicates (likely)"},
        {value: 10, icon: "⊕⊙⊙", text: "Evidence suggests"},
        {value: 1, icon: "⊙⊙⊙", text: "Evidence inadequate"},
        {value: -10, icon: "⊝⊝⊝", text: "Strong evidence supports no effect"},
        {value: NO_JUDGMENT, icon: "", text: "None"},
        {value: CUSTOM_JUDGMENT, icon: "", text: "Custom"},
    ],
    JudgmentSelector = observer(props => {
        const {value, handleSelect, helpText} = props,
            choicesList = props.summary ? summaryJudgmentChoices : judgmentChoices,
            choices = choicesList.map(d => {
                return {id: d.value, label: `${d.icon} ${d.text}`};
            }),
            label = props.summary ? "Judgment" : undefined;
        return (
            <SelectInput
                label={label}
                value={value}
                choices={choices}
                handleSelect={handleSelect}
                helpText={helpText}
            />
        );
    }),
    Judgment = observer(props => {
        const choices = props.summary ? summaryJudgmentChoices : judgmentChoices,
            choice = _.find(choices, {value: props.value});

        let {icon, text} = choice;

        if (choice.value === NO_JUDGMENT) {
            return null;
        }

        if (choice.value === CUSTOM_JUDGMENT) {
            icon = props.judgment.custom_judgment_icon;
            text = props.judgment.custom_judgment_label;
        }

        return (
            <div className="text-center">
                <p className="font-weight-bold" style={{fontSize: "1.5rem", lineHeight: 0.9}}>
                    {icon}
                </p>
                <p>
                    <em>{text}</em>
                </p>
            </div>
        );
    });

JudgmentSelector.propTypes = {
    value: PropTypes.number.isRequired,
    handleSelect: PropTypes.func.isRequired,
    summary: PropTypes.bool.isRequired,
    helpText: PropTypes.string,
};
Judgment.propTypes = {
    value: PropTypes.number.isRequired,
    judgment: PropTypes.object.isRequired,
    summary: PropTypes.bool.isRequired,
};

export {JudgmentSelector, Judgment};
