import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import SelectInput from "shared/components/SelectInput";

const judgementChoices = [
        {value: 30, icon: "⊕⊕⊕", text: "Robust"},
        {value: 20, icon: "⊕⊕⊙", text: "Moderate"},
        {value: 10, icon: "⊕⊙⊙", text: "Slight"},
        {value: 1, icon: "⊙⊙⊙", text: "Indeterminate"},
        {value: -10, icon: "⊝⊝⊝", text: "Evidence of no effect"},
        {value: 900, icon: "", text: "None"},
        {value: 910, icon: "", text: "Custom"},
    ],
    summaryJudgementChoices = [
        {value: 30, icon: "⊕⊕⊕", text: "Evidence demonstrates"},
        {value: 20, icon: "⊕⊕⊙", text: "Evidence indicates"},
        {value: 10, icon: "⊕⊙⊙", text: "Evidence suggests"},
        {value: 1, icon: "⊙⊙⊙", text: "Evidence inadequate"},
        {value: -10, icon: "⊝⊝⊝", text: "Strong evidence supports no effect"},
        {value: 900, icon: "", text: "None"},
        {value: 910, icon: "", text: "Custom"},
    ],
    JudgementSelector = observer(props => {
        const {value, handleSelect} = props,
            choicesList = props.summary ? summaryJudgementChoices : judgementChoices,
            choices = choicesList.map(d => {
                return {id: d.value, label: `${d.icon} ${d.text}`};
            });
        return <SelectInput value={value} choices={choices} handleSelect={handleSelect} />;
    }),
    Judgement = observer(props => {
        const choices = props.summary ? summaryJudgementChoices : judgementChoices,
            choice = _.find(choices, {value: props.value});
        return (
            <div className="text-center">
                <p className="font-weight-bold" style={{fontSize: "1.5rem", lineHeight: 0.9}}>
                    {choice.icon}
                </p>
                <p>
                    <em>{choice.text}</em>
                </p>
            </div>
        );
    });

JudgementSelector.propTypes = {
    value: PropTypes.number.isRequired,
    handleSelect: PropTypes.func.isRequired,
    summary: PropTypes.bool.isRequired,
};
Judgement.propTypes = {
    value: PropTypes.number.isRequired,
    summary: PropTypes.bool.isRequired,
};

export {JudgementSelector, Judgement};
