import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";

import {getViewTableComponent} from "../lookups";

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
        const Component = getViewTableComponent(table);
        return <Component store={tableStore} />;
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
