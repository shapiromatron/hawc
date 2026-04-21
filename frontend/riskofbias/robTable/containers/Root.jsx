import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Loading from "shared/components/Loading";

import AggregateGraph from "./AggregateGraph";
import RiskOfBiasDisplay from "./RiskOfBiasDisplay";

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
