import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import AggregateGraph from "./AggregateGraph";
import RiskOfBiasDisplay from "./RiskOfBiasDisplay";
import Loading from "shared/components/Loading";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchFullStudyIfNeeded();
    }

    render() {
        const {itemsLoaded} = this.props.store;
        return (
            <>
                {itemsLoaded ? (
                    <>
                        <AggregateGraph />
                        <hr />
                        <RiskOfBiasDisplay />
                    </>
                ) : (
                    <Loading />
                )}
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
