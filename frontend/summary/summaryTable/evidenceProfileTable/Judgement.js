import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import SelectInput from "shared/components/SelectInput";

import {NO_JUDGEMENT, CUSTOM_JUDGEMENT} from "./common";

const judgementChoices = [
        {value: 30, icon: "⊕⊕⊕", text: "Robust"},
        {value: 20, icon: "⊕⊕⊙", text: "Moderate"},
        {value: 10, icon: "⊕⊙⊙", text: "Slight"},
        {value: 1, icon: "⊙⊙⊙", text: "Indeterminate"},
        {value: -10, icon: "⊝⊝⊝", text: "Evidence of no effect"},
        {value: NO_JUDGEMENT, icon: "", text: "None"},
        {value: CUSTOM_JUDGEMENT, icon: "", text: "Custom"},
    ],
    summaryJudgementChoices = [
        {value: 30, icon: "⊕⊕⊕", text: "Evidence demonstrates"},
        {value: 20, icon: "⊕⊕⊙", text: "Evidence indicates (likely)"},
        {value: 10, icon: "⊕⊙⊙", text: "Evidence suggests"},
        {value: 1, icon: "⊙⊙⊙", text: "Evidence inadequate"},
        {value: -10, icon: "⊝⊝⊝", text: "Strong evidence supports no effect"},
        {value: NO_JUDGEMENT, icon: "", text: "None"},
        {value: CUSTOM_JUDGEMENT, icon: "", text: "Custom"},
    ],
    JudgementSelector = observer(props => {
        const {value, handleSelect, helpText} = props,
            choicesList = props.summary ? summaryJudgementChoices : judgementChoices,
            choices = choicesList.map(d => {
                return {id: d.value, label: `${d.icon} ${d.text}`};
            }),
            label = props.summary ? "Judgement" : undefined;
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
    Judgement = observer(props => {
        const choices = props.summary ? summaryJudgementChoices : judgementChoices,
            choice = _.find(choices, {value: props.value});

        let {icon, text} = choice;

        if (choice.value === NO_JUDGEMENT) {
            return null;
        }

        if (choice.value === CUSTOM_JUDGEMENT) {
            icon = props.judgement.custom_judgement_icon;
            text = props.judgement.custom_judgement_label;
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

JudgementSelector.propTypes = {
    value: PropTypes.number.isRequired,
    handleSelect: PropTypes.func.isRequired,
    summary: PropTypes.bool.isRequired,
    helpText: PropTypes.string,
};
Judgement.propTypes = {
    value: PropTypes.number.isRequired,
    judgement: PropTypes.object.isRequired,
    summary: PropTypes.bool.isRequired,
};

export {JudgementSelector, Judgement};
