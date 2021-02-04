import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import {TableType} from "../constants";
import GenericTable from "../genericTable/Table";

const getTableComponent = function(table) {
    if (table.table_type == TableType.GENERIC) {
        return GenericTable;
    } else {
        throw "Unknown table type";
    }
};

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchTable();
    }
    render() {
        const {hasTable, table, tableStore} = this.props.store;
        if (!hasTable) {
            return <Loading />;
        }
        const Component = getTableComponent(table);
        return <Component store={tableStore} />;
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
