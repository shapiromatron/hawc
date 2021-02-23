import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import h from "shared/utils/helpers";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import TextInput from "shared/components/TextInput";

const increaseFactors = [
        {key: 0, label: "No factors noted"},
        {key: 20, label: "Consistency"},
        {key: 30, label: "Dose - response gradient"},
        {key: 40, label: "Coherence of effects"},
        {key: 50, label: "Large or concerning magnitude of effect"},
        {key: 60, label: "Mechanistic evidence providing plausibility"},
        {key: 70, label: "Medium or high confidence studies"},
        {key: 10, label: "Other"},
    ],
    decreaseFactors = [
        {key: 0, label: "No factors noted"},
        {key: -20, label: "Unexplained inconsistency"},
        {key: -30, label: "Imprecision"},
        {key: -40, label: "Lack of expected coherence"},
        {key: -50, label: "Evidence demonstrating implausibility"},
        {key: -60, label: "Low confidence studies"},
        {key: 10, label: "Other"},
    ],
    FactorsForm = observer(props => {
        const {store, updateKey, content, increase} = props,
            choices = increase ? increaseFactors : decreaseFactors;

        return (
            <div>
                {choices.map(choice => {
                    const key = h.randomString(),
                        selectedIndex = _.findIndex(content.factors, d => d.key == choice.key);
                    return (
                        <div key={choice.key}>
                            <CheckboxInput
                                checked={selectedIndex >= 0}
                                label={choice.label}
                                onChange={() => store.toggleFactor(updateKey, choice.key)}
                            />
                            {selectedIndex >= 0 ? (
                                <TextInput
                                    name={key}
                                    value={content.factors[selectedIndex].text}
                                    onChange={e =>
                                        store.updateValue(
                                            `${updateKey}.factors[${selectedIndex}].text`,
                                            e.target.value
                                        )
                                    }
                                />
                            ) : null}
                        </div>
                    );
                })}
                <QuillTextInput
                    value={content.text}
                    onChange={value => store.updateValue(`${updateKey}.text`, value)}
                />
            </div>
        );
    }),
    FactorsCell = observer(props => {
        const {content} = props,
            _factors = increaseFactors.concat(decreaseFactors);
        return (
            <td>
                {content.factors.length > 0 ? (
                    <ul>
                        {content.factors.map((factor, index) => {
                            let label = _factors.find(_factor => _factor.key == factor.key).label,
                                html = `<em>${label}</em> - ` + factor.text;
                            return <li key={index} dangerouslySetInnerHTML={{__html: html}}></li>;
                        })}
                    </ul>
                ) : null}
                <div dangerouslySetInnerHTML={{__html: content.text}}></div>
            </td>
        );
    });

FactorsForm.propTypes = {
    store: PropTypes.func.isRequired,
    updateKey: PropTypes.string.isRequired,
    content: PropTypes.object.isRequired,
    increase: PropTypes.bool.isRequired,
};
FactorsCell.propTypes = {
    content: PropTypes.object.isRequired,
};

export {FactorsForm, FactorsCell};
