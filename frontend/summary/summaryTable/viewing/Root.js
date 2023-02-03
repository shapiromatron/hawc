import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
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
        return (
            <>
                <Component store={tableStore} />
                <div dangerouslySetInnerHTML={{__html: table.caption}} />
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
