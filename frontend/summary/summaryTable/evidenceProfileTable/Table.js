import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Judgement} from "./Judgement";
import {FactorsCell} from "./Factors";
import h from "shared/utils/helpers";

const subTitleStyle = {backgroundColor: "#f5f5f5"},
    NoDataRow = function() {
        return (
            <tr>
                <td colSpan={5}>
                    <em>No data available.</em>
                </td>
            </tr>
        );
    },
    EvidenceRow = observer(props => {
        const {row, index, rowSpan} = props;
        return (
            <tr>
                <td>
                    <div dangerouslySetInnerHTML={{__html: row.evidence.description}}></div>
                </td>
                <td>
                    <div dangerouslySetInnerHTML={{__html: row.summary.findings}}></div>
                </td>
                <FactorsCell content={row.certain_factors} />
                <FactorsCell content={row.uncertain_factors} />
                {index == 0 || rowSpan == 1 ? (
                    <td rowSpan={rowSpan > 1 ? rowSpan : null}>
                        <Judgement
                            value={row.judgement.judgement}
                            judgement={row.judgement}
                            summary={false}
                        />
                        <div dangerouslySetInnerHTML={{__html: row.judgement.description}}></div>
                    </td>
                ) : null}
            </tr>
        );
    });

EvidenceRow.propTypes = {
    row: PropTypes.object.isRequired,
};

const TextBlock = observer(props => {
    if (!h.hasInnerText(props.html)) {
        return null;
    }

    return (
        <>
            <p>
                <em>{props.label}:</em>&nbsp;
            </p>
            <div dangerouslySetInnerHTML={{__html: props.html}}></div>
        </>
    );
});

@observer
class SummaryCell extends Component {
    render() {
        const {settings, numSummaryRows} = this.props.store,
            {summary_judgement} = settings;

        return (
            <td rowSpan={numSummaryRows}>
                <Judgement
                    value={summary_judgement.judgement}
                    judgement={summary_judgement}
                    summary={true}
                />
                <TextBlock label="Primary basis" html={summary_judgement.description} />
                <TextBlock label="Human relevance" html={summary_judgement.human_relevance} />
                <TextBlock
                    label="Cross-stream coherence"
                    html={summary_judgement.cross_stream_coherence}
                />
                <TextBlock
                    label="Susceptible populations and lifestages"
                    html={summary_judgement.susceptibility}
                />
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
                    <th colSpan={5} style={subTitleStyle}>
                        {exposed_human.title}
                    </th>
                    <SummaryCell store={this.props.store} />
                </tr>
                {exposed_human.rows.length == 0 ? NoDataRow() : null}
                {exposed_human.rows.map((row, index) => (
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
                <tr style={subTitleStyle}>
                    <th colSpan={5}>{animal.title}</th>
                </tr>
                {animal.rows.length == 0 ? NoDataRow() : null}
                {animal.rows.map((row, index) => (
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
                <tr style={subTitleStyle}>
                    <th colSpan={5}>{mechanistic.title}</th>
                </tr>
                <tr>
                    <th>{mechanistic.col_header_1}</th>
                    <th colSpan={3}>Summary of key findings and interpretation</th>
                    <th>Judgment(s) and rationale</th>
                </tr>
                {mechanistic.rows.length == 0 ? NoDataRow() : null}
                {mechanistic.rows.map((row, index) => {
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
                        <th colSpan={5}>Evidence Summary and Interpretation</th>
                        <th rowSpan={2}>Inferences and Summary Judgment</th>
                    </tr>
                    <tr>
                        <th>Studies, outcomes, and confidence</th>
                        <th>Summary of key findings</th>
                        <th>Factors that increase certainty</th>
                        <th>Factors that decrease certainty</th>
                        <th>Judgment(s) and rationale</th>
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
