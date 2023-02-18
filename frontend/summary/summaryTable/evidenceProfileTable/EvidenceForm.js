import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";
import QuillTextInput from "shared/components/QuillTextInput";
import TextInput from "shared/components/TextInput";

import {CUSTOM_JUDGEMENT, HELP_TEXT} from "./common";
import {FactorsForm} from "./Factors";
import {JudgementSelector} from "./Judgement";

const EvidenceForm = observer(props => {
        const {store, contentType, createMethodName, judgementRowSpan} = props,
            {settings} = props.store;
        return (
            <>
                <CheckboxInput
                    label="Hide section?"
                    checked={settings[contentType].hide_content}
                    onChange={e => {
                        store.updateValue(`${contentType}.hide_content`, e.target.checked);
                    }}
                    helpText={HELP_TEXT.HIDE_CONTENT}
                    required
                />
                <div className={settings[contentType].hide_content ? "hidden" : null}>
                    <TextInput
                        name="title"
                        label="Section subheading"
                        value={settings[contentType].title}
                        onChange={e => store.updateValue(`${contentType}.title`, e.target.value)}
                        helpText={HELP_TEXT.SECTION_SUBHEADING}
                        required
                    />
                    <CheckboxInput
                        label="Merge judgement?"
                        checked={settings[contentType].merge_judgement}
                        onChange={e =>
                            store.updateValue(`${contentType}.merge_judgement`, e.target.checked)
                        }
                        helpText={HELP_TEXT.JUDGEMENT}
                        required
                    />
                    <table className="table table-sm table-bordered">
                        <colgroup>
                            <col width="18%" />
                            <col width="18%" />
                            <col width="18%" />
                            <col width="18%" />
                            <col width="18%" />
                            <col width="10%" />
                        </colgroup>
                        <thead>
                            <tr>
                                <th>
                                    Studies
                                    <HelpTextPopup
                                        title="Help-text"
                                        content="List references (optional: include hyperlinks to other HAWC visualizations) informing the outcome(s). If it makes sense to do so, summarize confidence in same free text space."
                                    />
                                </th>
                                <th>
                                    Summary of key findings
                                    <HelpTextPopup
                                        title="Help-text"
                                        content="Briefly describe the primary results on the outcome(s), including  any within-stream mechanistic evidence informing biological plausibility (e.g., precursor events linked to adverse outcomes). If sensitivity issues were identified, describe the impact on the reliability of the reported findings."
                                    />
                                </th>
                                <th>
                                    Factors that increase certainty
                                    <HelpTextPopup
                                        title="Help-text"
                                        content={`${HELP_TEXT.IRIS_HANDBOOK} For entries with a free text option,  summarize the evidence supporting the selected factor(s) in a few words (required). Note any other factors that increased certainty`}
                                    />
                                </th>
                                <th>
                                    Factors that decrease certainty
                                    <HelpTextPopup
                                        title="Help-text"
                                        content={`${HELP_TEXT.IRIS_HANDBOOK} For entries with a free text option,  summarize the evidence supporting the selected factor(s) in a few words (required). Note any other factors that decreased certainty`}
                                    />
                                </th>
                                <th>
                                    Evidence Synthesis Judgment(s)
                                    <HelpTextPopup
                                        title="Help-text"
                                        content={`${HELP_TEXT.IRIS_HANDBOOK} Summarize any important interpretations, and the primary basis for the judgment(s)`}
                                    />
                                </th>
                                <ActionsTh onClickNew={() => store[createMethodName]()} />
                            </tr>
                        </thead>
                        <tbody>
                            {settings[contentType].rows.length ? (
                                settings[contentType].rows.map((row, index) => {
                                    return (
                                        <EvidenceFormRow
                                            store={store}
                                            row={row}
                                            index={index}
                                            key={index}
                                            contentType={contentType}
                                            judgementRowSpan={judgementRowSpan}
                                        />
                                    );
                                })
                            ) : (
                                <tr>
                                    <td colSpan={6}>
                                        <TextInput
                                            name="no_content_text"
                                            value={settings[contentType].no_content_text}
                                            onChange={e =>
                                                store.updateValue(
                                                    `${contentType}.no_content_text`,
                                                    e.target.value
                                                )
                                            }
                                            helpText={HELP_TEXT.NO_CONTENT}
                                            required
                                        />
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </>
        );
    }),
    EvidenceFormRow = observer(props => {
        const {contentType, row, index, store, judgementRowSpan} = props;
        return (
            <tr>
                <td>
                    <QuillTextInput
                        value={row.evidence.description}
                        onChange={value =>
                            store.updateValue(
                                `${contentType}.rows[${index}].evidence.description`,
                                value
                            )
                        }
                    />
                </td>
                <td>
                    <QuillTextInput
                        value={row.summary.findings}
                        onChange={value =>
                            store.updateValue(
                                `${contentType}.rows[${index}].summary.findings`,
                                value
                            )
                        }
                    />
                </td>
                <td>
                    <FactorsForm
                        store={store}
                        updateKey={`${contentType}.rows[${index}].certain_factors`}
                        content={row.certain_factors}
                        isIncreasing={true}
                    />
                </td>
                <td>
                    <FactorsForm
                        store={store}
                        updateKey={`${contentType}.rows[${index}].uncertain_factors`}
                        content={row.uncertain_factors}
                        isIncreasing={false}
                    />
                </td>
                <td>
                    {index == 0 || judgementRowSpan == 1 ? (
                        <>
                            <JudgementSelector
                                value={row.judgement.judgement}
                                handleSelect={value =>
                                    store.updateValue(
                                        `${contentType}.rows[${index}].judgement.judgement`,
                                        parseInt(value)
                                    )
                                }
                                summary={false}
                            />
                            {row.judgement.judgement === CUSTOM_JUDGEMENT ? (
                                <>
                                    <TextInput
                                        name="custom_judgement_icon"
                                        label="Custom icon"
                                        value={row.judgement.custom_judgement_icon}
                                        onChange={e =>
                                            store.updateValue(
                                                `${contentType}.rows[${index}].judgement.custom_judgement_icon`,
                                                e.target.value
                                            )
                                        }
                                        required
                                    />
                                    <TextInput
                                        name="custom_judgement_label"
                                        label="Custom label"
                                        value={row.judgement.custom_judgement_label}
                                        onChange={e =>
                                            store.updateValue(
                                                `${contentType}.rows[${index}].judgement.custom_judgement_label`,
                                                e.target.value
                                            )
                                        }
                                        required
                                    />
                                </>
                            ) : null}
                            <QuillTextInput
                                value={row.judgement.description}
                                onChange={value =>
                                    store.updateValue(
                                        `${contentType}.rows[${index}].judgement.description`,
                                        value
                                    )
                                }
                            />
                        </>
                    ) : null}
                </td>
                <MoveRowTd
                    onMoveUp={() => store.moveRowUp(contentType, index)}
                    onMoveDown={() => store.moveRowDown(contentType, index)}
                    onDelete={() => store.deleteRow(contentType, index)}
                />
            </tr>
        );
    });

EvidenceForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default EvidenceForm;
