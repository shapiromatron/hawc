import React from "react";
import "react-tabs/style/react-tabs.css";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import DataTable from "shared/components/DataTable";

import Plot from "./Plot";

@inject("store")
@observer
class EndpointListApp extends React.Component {
    render() {
        const {store} = this.props;

        if (!store.hasDataset) {
            return <Loading />;
        }

        return (
            <div>
                <Plot />
                {/* <DataTable dataset={store.dataset} /> */}
            </div>
        );
    }
}
EndpointListApp.propTypes = {
    store: PropTypes.object,
};

export default EndpointListApp;
