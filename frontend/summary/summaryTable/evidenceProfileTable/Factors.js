import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import h from "shared/utils/helpers";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";

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
        {key: -70, label: "Interpretation limitations", displayLabel: true},
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
                                    <QuillTextInput
                                        label="Description"
                                        name={key}
                                        value={content.factors[selectedIndex].short_description}
                                        onChange={value =>
                                            store.updateValue(
                                                `${updateKey}.factors[${selectedIndex}].short_description`,
                                                value
                                            )
                                        }
                                    />
                                    <QuillTextInput
                                        label="Hover-over"
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
                                    <hr />
                                </>
                            ) : null}
                        </div>
                    );
                })}
                <hr />
                <QuillTextInput
                    label="Additional free text"
                    value={content.text}
                    onChange={value => store.updateValue(`${updateKey}.text`, value)}
                />
            </div>
        );
    }),
    FactorsCell = observer(props => {
        /*
        Users provide descriptive text in html using a wysiwyg editor. We update the text provided
        to inject the header-text if available, as well as the help-text popup, if available. We
        assume that the text starts and ends with <p> tags which are required for our regular
        expressions for content insertion.
        */
        const {content} = props,
            _factors = increaseFactors.concat(decreaseFactors),
            injectText = (block, injectionText) => block.replace(/^<p>/gm, `<p>${injectionText}`),
            injectPopup = (block, factorType, factor) => {
                if (h.hasInnerText(factor.long_description)) {
                    // popup is designed to be the same as the HelpTextPopup component.
                    const popup = `<i
                            class="ml-1 fa fa-fw fa-info-circle"
                            aria-hidden="true"
                            data-html="true"
                            data-toggle="popover"
                            title="${factorType.label}"
                            data-content="${_.escape(factor.long_description)}"></i>`;
                    block = block.replace(/<\/p>$/gm, `${popup}</p>`);
                }
                return block;
            };

        return (
            <td>
                {content.factors.length > 0 ? (
                    <ul>
                        {content.factors.map((factor, index) => {
                            let factorType = _factors.find(_factor => _factor.key == factor.key),
                                dashText =
                                    h.hasInnerText(factor.short_description) > 0 ? " - " : "",
                                labelText = `<em>${factorType.label}</em>${dashText}`,
                                html = factor.short_description;

                            // prefix label if it exists
                            if (factorType.displayLabel) {
                                html = injectText(factor.short_description, labelText);
                            }

                            // inject popup if it exists
                            html = injectPopup(html, factorType, factor);

                            return <li key={index} dangerouslySetInnerHTML={{__html: html}}></li>;
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
    store: PropTypes.object.isRequired,
    updateKey: PropTypes.string.isRequired,
    content: PropTypes.object.isRequired,
    increase: PropTypes.bool.isRequired,
};
FactorsCell.propTypes = {
    content: PropTypes.object.isRequired,
};

export {FactorsForm, FactorsCell};
