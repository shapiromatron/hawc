import {inject, observer} from "mobx-react";
import {toJS} from "mobx";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchTable();
    }
    render() {
        const {hasTable, table} = this.props.store;
        if (!hasTable) {
            return <Loading />;
        }
        return (
            <>
                <pre>{JSON.stringify(toJS(table), null, 2)}</pre>
                <p>TODO - build table!</p>
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
