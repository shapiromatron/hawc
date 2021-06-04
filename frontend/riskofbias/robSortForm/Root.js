import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import SortTable from "./SortTable";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

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

        return (
            <div className="riskofbias-display">
                <ScrollToErrorBox error={store.error} />
                <a
                    className="btn btn-primary"
                    href={`/rob/assessment/${store.config.assessment_id}/domain/create/`}>
                    <i className="fa fa-fw fa-plus"></i> Add domain
                </a>
                <SortTable />
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
