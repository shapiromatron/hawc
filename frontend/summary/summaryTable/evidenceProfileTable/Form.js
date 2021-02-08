import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import TextInput from "shared/components/TextInput";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import {JudgementSelector} from "./Judgement";

const EvidenceForm = observer(props => {
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
                            <th>Evidence</th>
                            <th>Increase factors</th>
                            <th>Decrease factors</th>
                            <th>Key findings</th>
                            <th>Judgement</th>
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
                    <p>....certain_factors</p>
                </td>
                <td>
                    <p>....uncertain_factors</p>
                </td>
                <td>
                    <QuillTextInput
                        label="Optional"
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
                            <th>Evidence</th>
                            <th>Summary</th>
                            <th>Judgement</th>
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
                        helpText="..."
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
