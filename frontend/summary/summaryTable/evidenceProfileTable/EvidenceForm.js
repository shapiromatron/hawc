import {observer} from "mobx-react";
import React from "react";
import PropTypes from "prop-types";

import HelpTextPopup from "shared/components/HelpTextPopup";
import TextInput from "shared/components/TextInput";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import {JudgmentSelector} from "./Judgment";
import {FactorsForm} from "./Factors";

import {CUSTOM_JUDGMENT, HELP_TEXT} from "./common";

const EvidenceForm = observer(props => {
        const {store, contentType, createMethodName, judgmentRowSpan} = props,
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
                        label="Merge judgment?"
                        checked={settings[contentType].merge_judgment}
                        onChange={e =>
                            store.updateValue(`${contentType}.merge_judgment`, e.target.checked)
                        }
                        helpText={HELP_TEXT.JUDGMENT}
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
                                    Studies, outcomes, and confidence
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
                                    Judgment(s) and rationale
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
                                            judgmentRowSpan={judgmentRowSpan}
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
        const {contentType, row, index, store, judgmentRowSpan} = props;
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
                        increase={true}
                    />
                </td>
                <td>
                    <FactorsForm
                        store={store}
                        updateKey={`${contentType}.rows[${index}].uncertain_factors`}
                        content={row.uncertain_factors}
                        increase={false}
                    />
                </td>
                <td>
                    {index == 0 || judgmentRowSpan == 1 ? (
                        <>
                            <JudgmentSelector
                                value={row.judgment.judgment}
                                handleSelect={value =>
                                    store.updateValue(
                                        `${contentType}.rows[${index}].judgment.judgment`,
                                        parseInt(value)
                                    )
                                }
                                summary={false}
                            />
                            {row.judgment.judgment === CUSTOM_JUDGMENT ? (
                                <>
                                    <TextInput
                                        name="custom_judgment_icon"
                                        label="Custom icon"
                                        value={row.judgment.custom_judgment_icon}
                                        onChange={e =>
                                            store.updateValue(
                                                `${contentType}.rows[${index}].judgment.custom_judgment_icon`,
                                                e.target.value
                                            )
                                        }
                                        required
                                    />
                                    <TextInput
                                        name="custom_judgment_label"
                                        label="Custom label"
                                        value={row.judgment.custom_judgment_label}
                                        onChange={e =>
                                            store.updateValue(
                                                `${contentType}.rows[${index}].judgment.custom_judgment_label`,
                                                e.target.value
                                            )
                                        }
                                        required
                                    />
                                </>
                            ) : null}
                            <QuillTextInput
                                value={row.judgment.description}
                                onChange={value =>
                                    store.updateValue(
                                        `${contentType}.rows[${index}].judgment.description`,
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
