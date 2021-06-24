import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

import MetricForm from "./MetricForm";
import ScoreFilterForm from "./ScoreFilterForm";
import ScoreList from "./ScoreList";

import "./Main.css";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.fetchRobSettings();
        this.props.store.fetchStudyTypes();
    }
    render() {
        const {store} = this.props,
            {error, isLoading} = store;

        if (isLoading) {
            return <Loading />;
        }

        return (
            <>
                <ScrollToErrorBox error={error} />
                <ScoreFilterForm />
                <MetricForm />
                <ScoreList />
            </>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
