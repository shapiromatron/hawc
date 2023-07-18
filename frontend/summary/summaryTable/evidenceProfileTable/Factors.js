import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import QuillTextInput from "shared/components/QuillTextInput";
import h from "shared/utils/helpers";

const increaseFactors = [
        {key: 0, label: "No factors noted", displayLabel: true},
        {key: 70, label: "All or most studies are medium or high confidence", displayLabel: true},
        {key: 20, label: "Consistency", displayLabel: true},
        {key: 30, label: "Dose-response gradient", displayLabel: true},
        {key: 50, label: "Large or concerning magnitude of effect", displayLabel: true},
        {key: 40, label: "Coherence", displayLabel: true},
        {key: 100, label: "Other", displayLabel: false},
    ],
    decreaseFactors = [
        {key: 0, label: "No factors noted", displayLabel: true},
        {key: -60, label: "All or most studies are low confidence", displayLabel: true},
        {key: -20, label: "Unexplained inconsistency", displayLabel: true},
        {key: -30, label: "Imprecision", displayLabel: true},
        {key: -80, label: "Concerns about biological significance", displayLabel: true},
        {key: -90, label: "Indirect outcome measures", displayLabel: true},
        {key: -40, label: "Lack of expected coherence", displayLabel: true},
        {key: -100, label: "Other", displayLabel: false},
    ],
    FactorsForm = observer(props => {
        const {store, updateKey, content, isIncreasing} = props,
            choices = isIncreasing ? increaseFactors : decreaseFactors;

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
        to inject the header-text if available, as well as the help-text popup, if available.
        */
        const {content, isIncreasing} = props,
            factorMap = new Map(content.factors.map(e => [e.key, e])),
            factors = isIncreasing ? increaseFactors : decreaseFactors,
            injectText = (block, injectionText) =>
                h.addOuterTag(block, "p").replace(/^<p>/gm, `<p>${injectionText}`),
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
                    block = h.addOuterTag(block, "p").replace(/<\/p>$/gm, `${popup}</p>`);
                }
                return block;
            };

        return (
            <td>
                {factorMap.size > 0 ? (
                    <ul>
                        {factors.map((factorType, index) => {
                            let factor = factorMap.get(factorType.key);
                            if (factor == undefined) {
                                return null;
                            }
                            let dashText =
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
    isIncreasing: PropTypes.bool.isRequired,
};
FactorsCell.propTypes = {
    content: PropTypes.object.isRequired,
    isIncreasing: PropTypes.bool.isRequired,
};

export {FactorsCell, FactorsForm};
