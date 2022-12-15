import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";

import Table from "./Table";

@observer
class TableForm extends Component {
    render() {
        const {store} = this.props;
        if (store.isFetching) {
            return <Loading />;
        }

        if (!store.hasData) {
            return (
                <Alert message="No data are available. Check your dataset settings on the 'data' tab." />
            );
        }

        return (
            <>
                <legend>Edit table</legend>
                <div className="float-right">
                    <button className="btn btn-light mx-1" onClick={store.createSubheader}>
                        <i className="fa fa-plus mr-1"></i>Add subheader
                    </button>
                    <button className="btn btn-light mx-1" onClick={store.createColumn}>
                        <i className="fa fa-plus mr-1"></i>Add column
                    </button>
                    <button className="btn btn-light mx-1" onClick={store.createRow}>
                        <i className="fa fa-plus mr-1"></i>Add row
                    </button>
                </div>
                <Table store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
