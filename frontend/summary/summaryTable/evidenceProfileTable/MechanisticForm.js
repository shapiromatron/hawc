import {observer} from "mobx-react";
import React from "react";
import PropTypes from "prop-types";

import HelpTextPopup from "shared/components/HelpTextPopup";
import TextInput from "shared/components/TextInput";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";

import {JUDGEMENT_HELP_TEXT, HIDE_CONTENT_HELP_TEXT, NO_CONTENT_HELP_TEXT} from "./common";

const MechanisticForm = observer(props => {
        const {store} = props,
            {mechanistic} = props.store.settings;
        return (
            <>
                <CheckboxInput
                    label="Hide section?"
                    checked={mechanistic.hide_content}
                    onChange={e => {
                        store.updateValue("mechanistic.hide_content", e.target.checked);
                    }}
                    helpText={HIDE_CONTENT_HELP_TEXT}
                    required
                />
                <div className={mechanistic.hide_content ? "hidden" : null}>
                    <TextInput
                        name="title"
                        label="Section subheading"
                        value={mechanistic.title}
                        onChange={e => store.updateValue("mechanistic.title", e.target.value)}
                        required
                    />
                    <TextInput
                        name="col_header"
                        label="Evidence header"
                        value={mechanistic.col_header_1}
                        onChange={e =>
                            store.updateValue("mechanistic.col_header_1", e.target.value)
                        }
                        required
                    />
                    <CheckboxInput
                        label="Merge judgement?"
                        checked={mechanistic.merge_judgement}
                        onChange={e =>
                            store.updateValue("mechanistic.merge_judgement", e.target.checked)
                        }
                        helpText={JUDGEMENT_HELP_TEXT}
                        required
                    />
                    <table className="table table-sm table-bordered">
                        <colgroup>
                            <col width="30%" />
                            <col width="30%" />
                            <col width="30%" />
                            <col width="10%" />
                        </colgroup>
                        <thead>
                            <tr>
                                <th>
                                    {mechanistic.col_header_1}
                                    <HelpTextPopup
                                        title="Help-text"
                                        content="Briefly describe the evidence or information analyzed, which may be subdivided as described in the “adding rows” instruction. Generally, cite or link evidence synthesis (e.g., for references; for detailed analysis). Does not have to be chemical-specific (e.g., read-across)."
                                    />
                                </th>
                                <th>
                                    Summary of key findings and interpretation
                                    <HelpTextPopup
                                        title="Help-text"
                                        content="Summary of expert interpretation of the body of evidence or information and supporting rationale. "
                                    />
                                </th>
                                <th>
                                    Judgment(s) and rationale
                                    <HelpTextPopup
                                        title="Help-text"
                                        content="Summary of findings across the body of evidence (may focus on or emphasize highly informative designs or findings), including key sources of uncertainty or identified limitations of the study designs tested (e.g., regarding the biological event or pathway being examined)."
                                    />
                                </th>
                                <ActionsTh onClickNew={() => store.createMechanisticRow()} />
                            </tr>
                        </thead>
                        <tbody>
                            {mechanistic.rows.length ? (
                                mechanistic.rows.map((row, index) => {
                                    return (
                                        <MechanisticFormRow
                                            store={store}
                                            row={row}
                                            index={index}
                                            key={index}
                                        />
                                    );
                                })
                            ) : (
                                <tr>
                                    <td colSpan={4}>
                                        <TextInput
                                            name="no_content_text"
                                            value={mechanistic.no_content_text}
                                            onChange={e =>
                                                store.updateValue(
                                                    "mechanistic.no_content_text",
                                                    e.target.value
                                                )
                                            }
                                            helpText={NO_CONTENT_HELP_TEXT}
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
    MechanisticFormRow = observer(props => {
        const {row, index, store} = props;
        return (
            <tr>
                <td>
                    <QuillTextInput
                        value={row.evidence.description}
                        onChange={value =>
                            store.updateValue(
                                `mechanistic.rows[${index}].evidence.description`,
                                value
                            )
                        }
                    />
                </td>
                <td>
                    <QuillTextInput
                        value={row.summary.findings}
                        onChange={value =>
                            store.updateValue(`mechanistic.rows[${index}].summary.findings`, value)
                        }
                    />
                </td>
                <td>
                    {index == 0 || store.numMechJudgementRowSpan == 1 ? (
                        <QuillTextInput
                            value={row.judgement.description}
                            onChange={value =>
                                store.updateValue(
                                    `mechanistic.rows[${index}].judgement.description`,
                                    value
                                )
                            }
                        />
                    ) : null}
                </td>
                <MoveRowTd
                    onMoveUp={() => store.moveRowUp("mechanistic", index)}
                    onMoveDown={() => store.moveRowDown("mechanistic", index)}
                    onDelete={() => store.deleteRow("mechanistic", index)}
                />
            </tr>
        );
    });

MechanisticForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default MechanisticForm;
