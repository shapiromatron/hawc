import React from "react";
import "react-tabs/style/react-tabs.css";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import DataTable from "shared/components/DataTable";

import Plot from "./Plot";
import Widgets from "./Widgets";

@inject("store")
@observer
class EndpointListApp extends React.Component {
    render() {
        const {store} = this.props;

        if (!store.plotData) {
            return <Loading />;
        }

        return (
            <div>
                <Widgets />
                <Plot />
                <p>
                    <b>{store.filteredData.length}</b> endpoints selected.
                </p>
                <DataTable dataset={store.filteredData} />
            </div>
        );
    }
}
EndpointListApp.propTypes = {
    store: PropTypes.object,
};

export default EndpointListApp;
