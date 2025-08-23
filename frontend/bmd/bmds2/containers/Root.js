import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import Loading from "/shared/components/Loading";

import Modals from "./Modals";
import TabContainer from "./TabContainer";

@inject("store")
@observer
class Root extends React.Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchData();
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
