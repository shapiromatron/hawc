import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import HelpTextPopup from "shared/components/HelpTextPopup";
import TextInput from "shared/components/TextInput";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import {JudgementSelector} from "./Judgement";

const JUDGEMENT_HELP_TEXT =
        "If judgements are merged, a single response is presented for all findings. Otherwise, each row will have it's own judgement and rationale.",
    EvidenceForm = observer(props => {
        const {store, contentType, createMethodName, judgementRowSpan} = props,
            {settings} = props.store;
        return (
            <div>
                <TextInput
                    name="title"
                    label="Subheading"
                    value={settings[contentType].title}
                    onChange={e => store.updateValue(`${contentType}.title`, e.target.value)}
                    required
                />
                <CheckboxInput
                    label="Merge judgement?"
                    checked={settings[contentType].merge_judgement}
                    onChange={e =>
                        store.updateValue(`${contentType}.merge_judgement`, e.target.checked)
                    }
                    helpText={JUDGEMENT_HELP_TEXT}
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
                                    content="List references (or link to locations) informing the outcome(s). If it makes sense to do so, summarize confidence in same free text space."
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
                                    content="For entries with a free text option,  summarize the evidence supporting the selected factor(s) in a few words (required). Note any other factors that increased certainty"
                                />
                            </th>
                            <th>
                                Factors that decrease certainty
                                <HelpTextPopup
                                    title="Help-text"
                                    content="For entries with a free text option,  summarize the evidence supporting the selected factor(s) in a few words (required). Note any other factors that decreased certainty"
                                />
                            </th>
                            <th>
                                Judgment(s) and rationale
                                <HelpTextPopup
                                    title="Help-text"
                                    content="Hyperlink to framework for drawing strength of evidence judgments. Summarize any important interpretations, and the primary basis for the judgment(s)"
                                />
                            </th>
                            <ActionsTh onClickNew={() => store[createMethodName]()} />
                        </tr>
                    </thead>
                    <tbody>
                        {settings[contentType].cell_rows.map((row, index) => {
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
                        })}
                    </tbody>
                </table>
            </div>
        );
    }),
    EvidenceFormRow = observer(props => {
        const {contentType, row, index, store, judgementRowSpan} = props;
        return (
            <tr>
                <td>
                    <QuillTextInput
                        label="Evidence"
                        value={row.evidence.evidence}
                        onChange={value =>
                            store.updateValue(
                                `${contentType}.cell_rows[${index}].evidence.evidence`,
                                value
                            )
                        }
                    />
                    <QuillTextInput
                        label="Confidence"
                        value={row.evidence.confidence}
                        onChange={value =>
                            store.updateValue(
                                `${contentType}.cell_rows[${index}].evidence.confidence`,
                                value
                            )
                        }
                    />
                    <QuillTextInput
                        label="Optional"
                        value={row.evidence.optional}
                        onChange={value =>
                            store.updateValue(
                                `${contentType}.cell_rows[${index}].evidence.optional`,
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
                                `${contentType}.cell_rows[${index}].summary.findings`,
                                value
                            )
                        }
                    />
                </td>
                <td>
                    <p>TODO - certain_factors</p>
                </td>
                <td>
                    <p>TODO - uncertain_factors</p>
                </td>
                <td>
                    {index == 0 || judgementRowSpan == 1 ? (
                        <>
                            <JudgementSelector
                                value={row.judgement.judgement}
                                handleSelect={value =>
                                    store.updateValue(
                                        `${contentType}.cell_rows[${index}].judgement.judgement`,
                                        parseInt(value)
                                    )
                                }
                                summary={false}
                            />
                            <QuillTextInput
                                value={row.judgement.description}
                                onChange={value =>
                                    store.updateValue(
                                        `${contentType}.cell_rows[${index}].judgement.description`,
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
    }),
    MechanisticForm = observer(props => {
        const {store} = props,
            {mechanistic} = props.store.settings;
        return (
            <div>
                <TextInput
                    name="title"
                    label="Subheading"
                    value={mechanistic.title}
                    onChange={e => store.updateValue("mechanistic.title", e.target.value)}
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
                                Biological events or pathways
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
                        {mechanistic.cell_rows.map((row, index) => {
                            return (
                                <MechanisticFormRow
                                    store={store}
                                    row={row}
                                    index={index}
                                    key={index}
                                />
                            );
                        })}
                    </tbody>
                </table>
            </div>
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
                                `mechanistic.cell_rows[${index}].evidence.description`,
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
                                `mechanistic.cell_rows[${index}].summary.findings`,
                                value
                            )
                        }
                    />
                </td>
                <td>
                    {index == 0 || store.numMechJudgementRowSpan == 1 ? (
                        <QuillTextInput
                            value={row.judgement.description}
                            onChange={value =>
                                store.updateValue(
                                    `mechanistic.cell_rows[${index}].judgement.description`,
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
    }),
    IntegrationForm = observer(props => {
        const {store} = props,
            {summary_judgement} = props.store.settings;

        return (
            <div className="form-row">
                <div className="col-md-12">
                    <JudgementSelector
                        value={summary_judgement.judgement}
                        handleSelect={value =>
                            store.updateValue("summary_judgement.judgement", parseInt(value))
                        }
                        summary={true}
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Description"
                        helpText="Enter the overall summary of expert interpretation across the assessed set of biological events, potential mechanisms of toxicity, or other analysis approach (e.g., AOP). Include the primary evidence supporting the interpretation(s).  Describe and substantiate the extent to which the evidence influences inferences across evidence streams. Characterize the limitations of the analyses and highlight data gaps. May have overlap with factors summarized for other streams"
                        value={summary_judgement.description}
                        onChange={value =>
                            store.updateValue("summary_judgement.description", value)
                        }
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Susceptibility"
                        helpText="..."
                        value={summary_judgement.susceptibility}
                        onChange={value =>
                            store.updateValue("summary_judgement.susceptibility", value)
                        }
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Human relevance"
                        helpText="..."
                        value={summary_judgement.human_relevance}
                        onChange={value =>
                            store.updateValue("summary_judgement.human_relevance", value)
                        }
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Cross-stream coherence"
                        helpText="..."
                        value={summary_judgement.cross_stream_coherence}
                        onChange={value =>
                            store.updateValue("summary_judgement.cross_stream_coherence", value)
                        }
                    />
                </div>
            </div>
        );
    });

@observer
class EvidenceProfileForm extends Component {
    render() {
        const {store} = this.props,
            {
                editTabIndex,
                editTabIndexUpdate,
                numEpiJudgementRowSpan,
                numAniJudgementRowSpan,
            } = store;
        return (
            <Tabs selectedIndex={editTabIndex} onSelect={tabIndex => editTabIndexUpdate(tabIndex)}>
                <TabList>
                    <Tab>Human</Tab>
                    <Tab>Animal</Tab>
                    <Tab>Mechanistic</Tab>
                    <Tab>Integration</Tab>
                </TabList>
                <TabPanel>
                    <EvidenceForm
                        store={store}
                        contentType={"exposed_human"}
                        createMethodName={"createHumanRow"}
                        judgementRowSpan={numEpiJudgementRowSpan}
                    />
                </TabPanel>
                <TabPanel>
                    <EvidenceForm
                        store={store}
                        contentType={"animal"}
                        createMethodName={"createAnimalRow"}
                        judgementRowSpan={numAniJudgementRowSpan}
                    />
                </TabPanel>
                <TabPanel>
                    <MechanisticForm store={store} />
                </TabPanel>
                <TabPanel>
                    <IntegrationForm store={store} />
                </TabPanel>
            </Tabs>
        );
    }
}

EvidenceProfileForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default EvidenceProfileForm;
