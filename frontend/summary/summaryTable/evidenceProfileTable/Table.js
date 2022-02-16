import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Judgment} from "./Judgment";
import {FactorsCell} from "./Factors";
import h from "shared/utils/helpers";

import {enablePopovers, disablePopovers} from "shared/components/HelpTextPopup";

const subTitleStyle = {backgroundColor: "#f5f5f5"},
    NoDataRow = function(no_content_text) {
        return (
            <tr>
                <td colSpan={5}>
                    <em>{no_content_text}</em>
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
                        <Judgment
                            value={row.judgment.judgment}
                            judgment={row.judgment}
                            summary={false}
                        />
                        <div dangerouslySetInnerHTML={{__html: row.judgment.description}}></div>
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
            {summary_judgment} = settings;

        return (
            <td rowSpan={numSummaryRows}>
                <Judgment
                    value={summary_judgment.judgment}
                    judgment={summary_judgment}
                    summary={true}
                />
                <TextBlock label="Primary basis" html={summary_judgment.description} />
                <TextBlock label="Human relevance" html={summary_judgment.human_relevance} />
                <TextBlock
                    label="Cross-stream coherence"
                    html={summary_judgment.cross_stream_coherence}
                />
                <TextBlock
                    label="Susceptible populations and lifestages"
                    html={summary_judgment.susceptibility}
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
        const {numEpiJudgmentRowSpan} = this.props.store,
            {exposed_human} = this.props.store.settings,
            show_summary = !this.props.store.settings.summary_judgment.hide_content;
        return (
            <>
                <tr>
                    <th colSpan={5} style={subTitleStyle}>
                        {exposed_human.title}
                    </th>
                    {show_summary ? <SummaryCell store={this.props.store} /> : null}
                </tr>
                {exposed_human.rows.length == 0 ? NoDataRow(exposed_human.no_content_text) : null}
                {exposed_human.rows.map((row, index) => (
                    <EvidenceRow
                        key={index}
                        row={row}
                        index={index}
                        rowSpan={numEpiJudgmentRowSpan}
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
        const {numAniJudgmentRowSpan} = this.props.store,
            {animal} = this.props.store.settings,
            show_summary =
                !this.props.store.settings.summary_judgment.hide_content &&
                this.props.store.settings.exposed_human.hide_content;
        return (
            <>
                <tr>
                    <th colSpan={5} style={subTitleStyle}>
                        {animal.title}
                    </th>
                    {show_summary ? <SummaryCell store={this.props.store} /> : null}
                </tr>
                {animal.rows.length == 0 ? NoDataRow(animal.no_content_text) : null}
                {animal.rows.map((row, index) => (
                    <EvidenceRow
                        key={index}
                        row={row}
                        index={index}
                        rowSpan={numAniJudgmentRowSpan}
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
        const {numMechJudgmentRowSpan} = this.props.store,
            {mechanistic} = this.props.store.settings,
            show_summary =
                !this.props.store.settings.summary_judgment.hide_content &&
                this.props.store.settings.exposed_human.hide_content &&
                this.props.store.settings.animal.hide_content;
        return (
            <>
                <tr>
                    <th colSpan={5} style={subTitleStyle}>
                        {mechanistic.title}
                    </th>
                    {show_summary ? <SummaryCell store={this.props.store} /> : null}
                </tr>
                <tr>
                    <th>{mechanistic.col_header_1}</th>
                    <th colSpan={3}>Summary of key findings and interpretation</th>
                    <th>Judgment(s) and rationale</th>
                </tr>
                {mechanistic.rows.length == 0 ? NoDataRow(mechanistic.no_content_text) : null}
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
                            {index == 0 || numMechJudgmentRowSpan == 1 ? (
                                <td rowSpan={index == 0 ? numMechJudgmentRowSpan : null}>
                                    <div
                                        dangerouslySetInnerHTML={{
                                            __html: row.judgment.description,
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
    constructor(props) {
        super(props);
        this.domNode = React.createRef();
    }
    componentDidMount() {
        /*
        Enable tooltips within the Table using the twitter bootstrap jQuery API
        after the  component has fully mounted. We can't use components for this since the
        tooltips are being added in text instead of using React components.
        */
        if (this.domNode.current) {
            const $el = $(this.domNode.current).find('[data-toggle="popover"]');
            enablePopovers($el);
        }
    }

    componentWillUnmount() {
        if (this.domNode.current) {
            const $el = $(this.domNode.current).find('[data-toggle="popover"]');
            disablePopovers($el);
        }
    }

    render() {
        const {store} = this.props,
            {exposed_human, animal, mechanistic, summary_judgment} = store.settings,
            hide_evidence =
                exposed_human.hide_content && animal.hide_content && mechanistic.hide_content;
        return hide_evidence && summary_judgment.hide_content ? null : (
            <table ref={this.domNode} className="summaryTable table table-bordered table-sm">
                {hide_evidence ? null : (
                    <colgroup>
                        <col style={{width: "15%"}}></col>
                        <col style={{width: "15%"}}></col>
                        <col style={{width: "15%"}}></col>
                        <col style={{width: "15%"}}></col>
                        <col style={{width: "15%"}}></col>
                        <col style={{width: "25%"}}></col>
                    </colgroup>
                )}
                <thead>
                    <tr>
                        {hide_evidence ? null : (
                            <th colSpan={5}>Evidence Summary and Interpretation</th>
                        )}
                        {summary_judgment.hide_content ? null : (
                            <th rowSpan={exposed_human.hide_content && animal.hide_content ? 1 : 2}>
                                Inferences and Summary Judgment
                            </th>
                        )}
                    </tr>
                    {exposed_human.hide_content && animal.hide_content ? null : (
                        <tr>
                            <th>Studies, outcomes, and confidence</th>
                            <th>Summary of key findings</th>
                            <th>Factors that increase certainty</th>
                            <th>Factors that decrease certainty</th>
                            <th>Judgment(s) and rationale</th>
                        </tr>
                    )}
                </thead>
                <tbody>
                    {exposed_human.hide_content ? null : <EpidemiologyEvidenceRows store={store} />}
                    {animal.hide_content ? null : <AnimalEvidenceRows store={store} />}
                    {mechanistic.hide_content ? null : <MechanisticEvidenceRows store={store} />}
                    {hide_evidence ? (
                        <tr>
                            <SummaryCell store={store} />
                        </tr>
                    ) : null}
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
