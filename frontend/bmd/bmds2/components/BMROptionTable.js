import PropTypes from "prop-types";
import React from "react";

class BMROptionTable extends React.Component {
    handleRowClick(bmrIndex) {
        this.props.handleModalDisplay(bmrIndex);
    }
    render() {
        return (
            <div className="col-md-6">
                <h4>Benchmark modeling responses</h4>
                <table className="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th style={{width: "30%"}}>Type</th>
                            <th style={{width: "20%"}}>Value</th>
                            <th style={{width: "25%"}}>Confidence level</th>
                            <th style={{width: "25%"}}>View</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <td colSpan="4">
                                All models will be run using the selected BMRs, if appropriate for
                                that particular model type.
                            </td>
                        </tr>
                    </tfoot>
                    <tbody>
                        {this.props.bmrs.map((bmr, i) => {
                            return (
                                <tr key={i}>
                                    <td>{bmr.type}</td>
                                    <td>{bmr.value}</td>
                                    <td>{bmr.confidence_level}</td>
                                    <td>
                                        <button
                                            type="button"
                                            className="btn btn-link"
                                            onClick={this.handleRowClick.bind(this, i)}>
                                            View
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        );
    }
}

BMROptionTable.propTypes = {
    handleModalDisplay: PropTypes.func.isRequired,
    bmrs: PropTypes.array.isRequired,
};

export default BMROptionTable;
