import PropTypes from "prop-types";
import React from "react";

import ModelOptionOverrideList from "../containers/ModelOptionOverrideList";

class ModelOptionTable extends React.Component {
    constructor(props) {
        super(props);
        this.modelSelector = React.createRef();
    }

    render() {
        const {models} = this.props;
        return (
            <div className="col-6">
                <h4>Model options</h4>
                <table className="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th style={{width: "25%"}}>Model name</th>
                            <th style={{width: "60%"}}>Non-default settings</th>
                            <th style={{width: "15%"}}>View</th>
                        </tr>
                    </thead>
                    <tbody>
                        {models.map((d, i) => {
                            return (
                                <tr key={i}>
                                    <td>{d.name}</td>
                                    <td>
                                        <ModelOptionOverrideList index={i} />
                                    </td>
                                    <td>
                                        <button
                                            type="button"
                                            className="btn btn-link"
                                            onClick={() => this.props.handleModalDisplay(i)}>
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

ModelOptionTable.propTypes = {
    dataType: PropTypes.string.isRequired,
    handleModalDisplay: PropTypes.func.isRequired,
    models: PropTypes.array.isRequired,
    allOptions: PropTypes.array.isRequired,
};

export default ModelOptionTable;
