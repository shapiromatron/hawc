import {bmdLabelText} from "bmd/common/constants";
import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";

let getColWidths = function (numBmrs) {
        switch (numBmrs) {
            case 1:
                return {
                    name: "20%",
                    nums: "14%",
                    view: "10%",
                };
            case 2:
                return {
                    name: "16%",
                    nums: "11%",
                    view: "7%",
                };
            case 3:
                return {
                    name: "12%",
                    nums: "9%",
                    view: "7%",
                };
            default:
                return {
                    name: "1%",
                    nums: "1%",
                    view: "1%",
                };
        }
    },
    binModels = function (models) {
        return _.chain(models).groupBy("model_index").values().value();
    };

class OutputTable extends React.Component {
    handleRowClick(models) {
        this.props.handleModal(models);
    }

    handleMouseOver(model, evt) {
        if (!evt) return;
        evt.stopPropagation();
        evt.nativeEvent.stopImmediatePropagation();
        this.props.handleModelHover(model);
    }

    handleMouseOut(evt) {
        if (!evt) return;
        evt.stopPropagation();
        evt.nativeEvent.stopImmediatePropagation();
        this.props.handleModelNoHover();
    }

    renderRow(models) {
        let first = models[0],
            bmds = _.chain(models)
                .map((d, i) => {
                    return [
                        <td
                            key={i + "bmd"}
                            onMouseOver={this.handleMouseOver.bind(this, d)}
                            onMouseOut={this.handleMouseOut.bind(this)}>
                            {d.output.BMD}
                        </td>,
                        <td
                            key={i + "bmdl"}
                            onMouseOver={this.handleMouseOver.bind(this)}
                            onMouseOut={this.handleMouseOut.bind(this)}>
                            {d.output.BMDL}
                        </td>,
                    ];
                })
                .flattenDeep()
                .value(),
            id = _.includes(_.map(models, "id"), this.props.selectedModelId)
                ? "bmd_selected_model"
                : "";

        return (
            <tr
                key={first.id}
                onMouseOver={this.handleMouseOver.bind(this, first)}
                onMouseOut={this.handleMouseOut.bind(this)}
                id={id}>
                <td>{first.name}</td>
                <td>{first.output.p_value4}</td>
                <td>{first.output.AIC}</td>
                {bmds}
                <td>{first.output.residual_of_interest}</td>
                <td>
                    <button
                        type="button"
                        className="btn btn-link"
                        onClick={this.handleRowClick.bind(this, models)}>
                        View
                    </button>
                </td>
            </tr>
        );
    }

    renderHeader() {
        let widths = getColWidths(this.props.bmrs.length),
            ths = _.chain(this.props.bmrs)
                .map((d, i) => {
                    let lbl = bmdLabelText(d);
                    return [
                        <th key={i + "bmd"} style={{width: widths.nums}}>
                            BMD
                            <br />
                            <span>({lbl})</span>
                        </th>,
                        <th key={i + "bmdl"} style={{width: widths.nums}}>
                            BMDL
                            <br />
                            <span>({lbl})</span>
                        </th>,
                    ];
                })
                .flattenDeep()
                .value();

        return (
            <tr>
                <th style={{width: widths.name}}>Model</th>
                <th style={{width: widths.nums}}>
                    Global <br />
                    <i>p</i>-value
                </th>
                <th style={{width: widths.nums}}>AIC</th>
                {ths}
                <th style={{width: widths.nums}}>Residual of interest</th>
                <th style={{width: widths.view}}>Output</th>
            </tr>
        );
    }

    render() {
        if (this.props.models.length === 0) {
            return null;
        }

        let binnedModels = binModels(this.props.models);

        return (
            <table className="table table-sm">
                <thead>{this.renderHeader.bind(this)()}</thead>
                <tfoot>
                    <tr>
                        <td colSpan="100">Selected model (if any) highlighted in yellow</td>
                    </tr>
                </tfoot>
                <tbody style={{cursor: "pointer"}}>
                    {binnedModels.map(this.renderRow.bind(this))}
                </tbody>
            </table>
        );
    }
}

OutputTable.propTypes = {
    models: PropTypes.array.isRequired,
    bmrs: PropTypes.array.isRequired,
    handleModal: PropTypes.func.isRequired,
    handleModelHover: PropTypes.func.isRequired,
    handleModelNoHover: PropTypes.func.isRequired,
    selectedModelId: PropTypes.number,
};

export default OutputTable;
