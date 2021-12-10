import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Alert from "shared/components/Alert";
import ColumnForm from "./components/ColumnForm";
import Loading from "shared/components/Loading";
import RowForm from "./components/RowForm";
import Table from "./Table";

@observer
class TableForm extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchData();
    }
    render() {
        const {store} = this.props;
        if (store.isFetchingData) {
            return <Loading />;
        }

        if (!store.hasData) {
            return (
                <Alert message="No data are available. Studies must be published and have at least one endpoint to be available for this summary table." />
            );
        }

        return (
            <>
                <h4>Editing table</h4>
                <div className="float-right">
                    <button className="btn btn-light mx-1" onClick={store.createColumn}>
                        <i className="fa fa-plus mr-1"></i>Add column
                    </button>
                    <button className="btn btn-light mx-1" onClick={store.createRow}>
                        <i className="fa fa-plus mr-1"></i>Add row
                    </button>
                </div>
                <p className="text-muted">Help text... </p>
                {store.showRowCreateForm ? <RowForm store={store} /> : null}
                {store.showColumnCreateForm ? <ColumnForm store={store} /> : null}
                <Table store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
