import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";

import Header from "./Header";
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
            <div>
                <Header />
                {itemsLoaded ? (
                    <>
                        <AggregateGraph />
                        <hr />
                        <RiskOfBiasDisplay />
                    </>
                ) : (
                    <Loading />
                )}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
