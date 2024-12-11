import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import Table from "./Table";

@inject("store")
@observer
class DatasetTable extends React.Component {
    render() {
        const {store} = this.props,
            datasetTableProps = store.datasetTableProps;

        return <Table {...datasetTableProps} />;
    }
}
DatasetTable.propTypes = {
    store: PropTypes.object,
};

export default DatasetTable;
