import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Judgement} from "./Judgement";

const NoDataRow = function() {
        return (
            <tr>
                <td colSpan={5}>
                    <em>No data available.</em>
                </td>
            </tr>
        );
    },
    EvidenceHeaderRow = function() {
        return (
            <tr>
                <th>Studies and confidence</th>
                <th>Factors that increase certainty</th>
                <th>Factors that decrease certainty</th>
                <th>Summary and key findings</th>
                <th>Evidence stream judgement</th>
            </tr>
        );
    },
    EvidenceRow = observer(props => {
        const {row, index, rowSpan} = props;
        return (
            <tr>
                <td>
                    <div dangerouslySetInnerHTML={{__html: row.evidence.evidence}}></div>
                    <div dangerouslySetInnerHTML={{__html: row.evidence.confidence}}></div>
                    <div dangerouslySetInnerHTML={{__html: row.evidence.optional}}></div>
                </td>
                <td>
                    {row.certain_factors.factors.length > 0 ? (
                        <ul>
                            {row.certain_factors.factors.map((factor, index) => {
                                return (
                                    <li key={index} dangerouslySetInnerHTML={{__html: factor}}></li>
                                );
                            })}
                        </ul>
                    ) : (
                        <i>No factors available.</i>
                    )}
                </td>
                <td>
                    {row.uncertain_factors.factors.length > 0 ? (
                        <ul>
                            {row.uncertain_factors.factors.map((factor, index) => {
                                return (
                                    <li key={index} dangerouslySetInnerHTML={{__html: factor}}></li>
                                );
                            })}
                        </ul>
                    ) : (
                        <i>No factors available.</i>
                    )}
                </td>
                <td>
                    <div dangerouslySetInnerHTML={{__html: row.summary.findings}}></div>
                </td>
                {index == 0 || rowSpan == 1 ? (
                    <td rowSpan={rowSpan > 1 ? rowSpan : null}>
                        <Judgement value={row.judgement.judgement} summary={false} />
                        <div dangerouslySetInnerHTML={{__html: row.judgement.description}}></div>
                    </td>
                ) : null}
            </tr>
        );
    });

EvidenceRow.propTypes = {
    row: PropTypes.object.isRequired,
};

@observer
class SummaryCell extends Component {
    render() {
        const {settings, numSummaryRows} = this.props.store,
            {summary_judgement} = settings;

        return (
            <td rowSpan={numSummaryRows}>
                <Judgement value={summary_judgement.judgement} summary={true} />
                <p>
                    <em>Primary basis:</em>
                </p>
                <div dangerouslySetInnerHTML={{__html: summary_judgement.description}}></div>
                <p>
                    <em>Human relevance:</em>
                </p>
                <div dangerouslySetInnerHTML={{__html: summary_judgement.human_relevance}}></div>
                <p>
                    <em>Cross-stream coherence:</em>
                </p>
                <div
                    dangerouslySetInnerHTML={{
                        __html: summary_judgement.cross_stream_coherence,
                    }}></div>
                <p>
                    <em>Susceptible populations and lifestages:</em>
                </p>
                <div dangerouslySetInnerHTML={{__html: summary_judgement.susceptibility}}></div>
            </td>
        );
    }
}
SummaryCell.propTypes = {
    store: PropTypes.object.isRequired,
};

@observer
class EpidemiologyEvidenceRows extends Component {
    render() {
        const {numEpiJudgementRowSpan} = this.props.store,
            {exposed_human} = this.props.store.settings;
        return (
            <>
                <tr>
                    <th colSpan={5}>{exposed_human.title}</th>
                    <SummaryCell store={this.props.store} />
                </tr>
                <EvidenceHeaderRow />
                {exposed_human.cell_rows.length == 0 ? NoDataRow() : null}
                {exposed_human.cell_rows.map((row, index) => (
                    <EvidenceRow
                        key={index}
                        row={row}
                        index={index}
                        rowSpan={numEpiJudgementRowSpan}
                    />
                ))}
            </>
        );
    }
}

EpidemiologyEvidenceRows.propTypes = {
    store: PropTypes.object.isRequired,
};

@observer
class AnimalEvidenceRows extends Component {
    render() {
        const {numAniJudgementRowSpan} = this.props.store,
            {animal} = this.props.store.settings;
        return (
            <>
                <tr>
                    <th colSpan={5}>{animal.title}</th>
                </tr>
                <EvidenceHeaderRow />
                {animal.cell_rows.length == 0 ? NoDataRow() : null}
                {animal.cell_rows.map((row, index) => (
                    <EvidenceRow
                        key={index}
                        row={row}
                        index={index}
                        rowSpan={numAniJudgementRowSpan}
                    />
                ))}
            </>
        );
    }
}

AnimalEvidenceRows.propTypes = {
    store: PropTypes.object.isRequired,
};

@observer
class MechanisticEvidenceRows extends Component {
    render() {
        const {numMechJudgementRowSpan} = this.props.store,
            {mechanistic} = this.props.store.settings;
        return (
            <>
                <tr>
                    <th colSpan={5}>{mechanistic.title}</th>
                </tr>
                <tr>
                    <th>Biological events or pathways</th>
                    <th colSpan={3}>Summary of key findings, interpretation, and limitations</th>
                    <th>Evidence stream judgement</th>
                </tr>
                {mechanistic.cell_rows.length == 0 ? NoDataRow() : null}
                {mechanistic.cell_rows.map((row, index) => {
                    return (
                        <tr key={index}>
                            <td>
                                <div
                                    dangerouslySetInnerHTML={{
                                        __html: row.evidence.description,
                                    }}></div>
                            </td>
                            <td colSpan={3}>
                                <div dangerouslySetInnerHTML={{__html: row.summary.findings}}></div>
                            </td>
                            {index == 0 || numMechJudgementRowSpan == 1 ? (
                                <td rowSpan={index == 0 ? numMechJudgementRowSpan : null}>
                                    <div
                                        dangerouslySetInnerHTML={{
                                            __html: row.judgement.description,
                                        }}></div>
                                </td>
                            ) : null}
                        </tr>
                    );
                })}
            </>
        );
    }
}

MechanisticEvidenceRows.propTypes = {
    store: PropTypes.object.isRequired,
};

@observer
class Table extends Component {
    render() {
        const {store} = this.props;
        return (
            <table className="summaryTable table table-bordered table-sm">
                <colgroup>
                    <col style={{width: "15%"}}></col>
                    <col style={{width: "15%"}}></col>
                    <col style={{width: "15%"}}></col>
                    <col style={{width: "15%"}}></col>
                    <col style={{width: "15%"}}></col>
                    <col style={{width: "25%"}}></col>
                </colgroup>
                <thead>
                    <tr>
                        <th colSpan={5}>Evidence stream summary and interpretation</th>
                        <th>Evidence integration summary judgement</th>
                    </tr>
                </thead>
                <tbody>
                    <EpidemiologyEvidenceRows store={store} />
                    <AnimalEvidenceRows store={store} />
                    <MechanisticEvidenceRows store={store} />
                </tbody>
            </table>
        );
    }
}

Table.defaultProps = {
    forceReadOnly: false,
};

Table.propTypes = {
    store: PropTypes.object.isRequired,
    forceReadOnly: PropTypes.bool,
};

export default Table;
