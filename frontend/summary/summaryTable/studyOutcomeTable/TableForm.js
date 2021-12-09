import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Table from "./Table";

@observer
class TableForm extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchData();
    }
    render() {
        const {store} = this.props;
        return (
            <>
                <h4>Editing table</h4>
                <div className="float-right">
                    <button className="btn btn-light mx-1" onClick={store.addColumn}>
                        <i className="fa fa-plus mr-1"></i>Add column
                    </button>
                    <button className="btn btn-light mx-1" onClick={store.addRow}>
                        <i className="fa fa-plus mr-1"></i>Add row
                    </button>
                </div>
                <p className="text-muted">Help text... </p>
                <Table store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
