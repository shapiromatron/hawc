import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import GenericTable from "./table/GenericTable";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchTable();
        this.props.store.fetchCells();
    }
    render() {
        const {hasTable, hasCells} = this.props.store;
        if (!hasTable || !hasCells) {
            return <Loading />;
        }
        return (
            <>
                <GenericTable />
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
