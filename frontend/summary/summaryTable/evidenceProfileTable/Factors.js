import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import h from "shared/utils/helpers";
import HelpTextPopup from "shared/components/HelpTextPopup";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import TextInput from "shared/components/TextInput";

const increaseFactors = [
        {key: 0, label: "No factors noted", displayLabel: true},
        {key: 20, label: "Consistency", displayLabel: true},
        {key: 30, label: "Dose - response gradient", displayLabel: true},
        {key: 40, label: "Coherence of effects", displayLabel: true},
        {key: 50, label: "Large or concerning magnitude of effect", displayLabel: true},
        {key: 60, label: "Mechanistic evidence providing plausibility", displayLabel: true},
        {key: 70, label: "Medium or high confidence studies", displayLabel: true},
        {key: 100, label: "Other", displayLabel: false},
    ],
    decreaseFactors = [
        {key: 0, label: "No factors noted", displayLabel: true},
        {key: -20, label: "Unexplained inconsistency", displayLabel: true},
        {key: -30, label: "Imprecision", displayLabel: true},
        {key: -40, label: "Lack of expected coherence", displayLabel: true},
        {key: -50, label: "Evidence demonstrating implausibility", displayLabel: true},
        {key: -60, label: "Low confidence studies", displayLabel: true},
        {key: -100, label: "Other", displayLabel: false},
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
                                <>
                                    <TextInput
                                        label="Short description"
                                        name={key}
                                        value={content.factors[selectedIndex].short_description}
                                        onChange={e =>
                                            store.updateValue(
                                                `${updateKey}.factors[${selectedIndex}].short_description`,
                                                e.target.value
                                            )
                                        }
                                    />
                                    <QuillTextInput
                                        label="Verbose description"
                                        helpText="Shows up as hover text"
                                        value={
                                            content.factors[selectedIndex].long_description ||
                                            "<p></p>"
                                        }
                                        onChange={value =>
                                            store.updateValue(
                                                `${updateKey}.factors[${selectedIndex}].long_description`,
                                                value
                                            )
                                        }
                                    />
                                </>
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
                            let factorType = _factors.find(_factor => _factor.key == factor.key),
                                html = factorType.displayLabel
                                    ? `<em>${factorType.label}</em> - ` + factor.short_description
                                    : factor.short_description;
                            return (
                                <li key={index}>
                                    <span dangerouslySetInnerHTML={{__html: html}}></span>
                                    <HelpTextPopup
                                        title={factorType.label}
                                        content={factor.long_description}
                                    />
                                </li>
                            );
                        })}
                    </ul>
                ) : null}
                {h.hasInnerText(content.text) ? (
                    <div dangerouslySetInnerHTML={{__html: content.text}}></div>
                ) : null}
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
