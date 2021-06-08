import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import SortTable from "./SortTable";
import Loading from "shared/components/Loading";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.setConfig("config");
        this.props.store.fetchRoBData();
    }

    render() {
        let {store} = this.props;
        if (store.dataLoaded === false) {
            return <Loading />;
        }

        return <SortTable />;
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
