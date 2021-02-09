import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import h from "shared/utils/helpers";

const increaseFactors = [
        {key: 10, label: "No factors noted"},
        {key: 20, label: "Consistency"},
        {key: 30, label: "Dose - response gradient"},
        {key: 40, label: "Coherence of effects"},
        {key: 50, label: "Large or concerning magnitude of effect"},
        {key: 60, label: "Mechanistic evidence providing plausibility"},
        {key: 70, label: "Medium or high confidence studies"},
        {key: 80, label: "Other"},
    ],
    decreaseFactors = [
        {key: -10, label: "No factors noted"},
        {key: -20, label: "Unexplained inconsistency"},
        {key: -30, label: "Imprecision"},
        {key: -40, label: "Lack of expected coherence"},
        {key: -50, label: "Evidence demonstrating implausibility"},
        {key: -60, label: "Low confidence studies"},
        {key: -70, label: "Other"},
    ],
    FactorListForm = observer(props => {
        const {values, handleSelect, increase} = props,
            choices = increase ? increaseFactors : decreaseFactors;
        return (
            <div>
                {choices.map(choice => {
                    const id = `factor_${choice.key}_${h.randomString()}`;
                    return (
                        <div className="form-check" key={id}>
                            <input
                                className="form-check-input"
                                type="checkbox"
                                value={choice.key}
                                id={id}
                            />
                            <label className="form-check-label" htmlFor={id}>
                                {choice.label}
                            </label>
                        </div>
                    );
                })}
            </div>
        );
    }),
    FactorList = observer(props => {});

FactorListForm.propTypes = {
    values: PropTypes.number.isRequired,
    handleSelect: PropTypes.func.isRequired,
    increase: PropTypes.bool.isRequired,
};
FactorList.propTypes = {
    values: PropTypes.number.isRequired,
    increase: PropTypes.bool.isRequired,
};

export {FactorListForm, FactorList};
