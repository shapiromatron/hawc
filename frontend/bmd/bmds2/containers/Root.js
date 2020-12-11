import React from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";

import TabContainer from "./TabContainer";
import Modals from "./Modals";

@inject("store")
@observer
class Root extends React.Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchEndpoint();
        store.fetchSessionSettings();
    }
    render() {
        const {store} = this.props;
        if (store.isReady === false) {
            return <Loading />;
        }

        return (
            <>
                <TabContainer />
                <Modals />
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
