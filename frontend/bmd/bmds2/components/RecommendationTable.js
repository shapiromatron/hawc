import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";

class RecommendationTable extends React.Component {
    renderModelTd(d) {
        return (
            <td>
                <h4>{d.name}</h4>
                <b>AIC: </b>
                {d.output.AIC}
                <br />
                <b>BMD: </b>
                {d.output.BMD}
                <br />
                <b>BMDL: </b>
                {d.output.BMDL}
                <br />
            </td>
        );
    }

    renderWarningTd(d) {
        let inner = [];
        if (d.logic_notes[0].length > 0) {
            inner.push(
                <div key={0}>
                    <b>Warnings</b>
                    <ul>
                        {d.logic_notes[0].map((d2, i) => (
                            <li key={i}>{d2}</li>
                        ))}
                    </ul>
                </div>
            );
        }
        if (d.logic_notes[1].length > 0) {
            inner.push(
                <div key={1}>
                    <b>Questionable warnings</b>
                    <ul>
                        {d.logic_notes[1].map((d2, i) => (
                            <li key={i}>{d2}</li>
                        ))}
                    </ul>
                </div>
            );
        }
        if (d.logic_notes[2].length > 0) {
            inner.push(
                <div key={2}>
                    <b>Serious warnings</b>
                    <ul>
                        {d.logic_notes[2].map((d2, i) => (
                            <li key={i}>{d2}</li>
                        ))}
                    </ul>
                </div>
            );
        }
        if (inner.length === 0) {
            inner.push(<i key={3}>No warnings were found.</i>);
        }
        return <td>{inner}</td>;
    }

    renderLogicBatch(d) {
        let cls, txt;
        switch (d.logic_bin) {
            case 0:
                cls = "badge badge-success bmd_recommendation";
                txt = "Valid";
                break;
            case 1:
                cls = "badge badge-warning bmd_recommendation";
                txt = "Questionable";
                break;
            case 2:
                cls = "badge badge-important bmd_recommendation";
                txt = "Failure";
                break;
        }
        return <p className={cls}>{txt}</p>;
    }

    renderRecommendationTd(d) {
        let txts = [];

        if (d.recommended) {
            txts.push(
                `Recommended best-fitting model, based on the lowest ${d.recommended_variable} from valid models.`
            );
        }

        if (this.props.selectedModelId === d.id) {
            txts.push("Selected as the best-fitting model by the user.");
        }

        return (
            <td>
                {this.renderLogicBatch(d)}
                <p>
                    <b>{txts.join(" ")}</b>
                </p>
            </td>
        );
    }

    renderRow(d, i) {
        let tdId = "";

        if (d.recommended) {
            tdId = "bmd_recommended_model";
        }

        if (this.props.selectedModelId === d.id) {
            tdId = "bmd_selected_model";
        }

        return (
            <tr key={i} id={tdId}>
                {this.renderModelTd(d)}
                {this.renderWarningTd(d)}
                {this.renderRecommendationTd(d)}
            </tr>
        );
    }

    render() {
        return (
            <table className="table table-hover table-sm">
                <thead>
                    <tr>
                        <th style={{width: "15%"}}>Model</th>
                        <th style={{width: "60%"}}>Warnings</th>
                        <th style={{width: "25%"}}>Recommendation</th>
                    </tr>
                </thead>
                <tfoot>
                    <tr>
                        <td colSpan="3">
                            <p>
                                The recommended model (if any) in shown in green. The user-selected
                                best-fitting model (if any) in shown in yellow.
                            </p>
                        </td>
                    </tr>
                </tfoot>
                <tbody>
                    {_.chain(this.props.models)
                        .sortBy("logic_bin")
                        .map(this.renderRow.bind(this))
                        .value()}
                </tbody>
            </table>
        );
    }
}

RecommendationTable.propTypes = {
    models: PropTypes.array.isRequired,
    selectedModelId: PropTypes.number,
};

export default RecommendationTable;
