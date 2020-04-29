import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";
import MetricForm from "../MetricForm";
import MetricSelect from "../MetricSelect";
import ScoreList from "../ScoreList";
import ScoreSelect from "../ScoreSelect";
import StudyTypeSelect from "../StudyTypeSelect";

import "./Root.css";

@inject("store")
@observer
class Root extends Component {
    componentDidMount() {
        this.props.store.setConfig("config");
        this.props.store.fetchMetricOptions();
        this.props.store.fetchScoreOptions();
        this.props.store.fetchStudyTypeOptions();
    }
    render() {
        const {error, isLoading} = this.props.store;

        if (isLoading) {
            return <Loading />;
        }

        return (
            <div>
                <ScrollToErrorBox error={error} />
                <div className="container-fluid cleanStudyMetricForm">
                    <div className="span6">
                        <MetricSelect />
                        <div>
                            <button
                                className="btn btn-primary space"
                                onClick={() => {
                                    this.props.store.fetchScores();
                                }}>
                                Load responses
                            </button>
                            <button
                                className="btn space"
                                onClick={() => {
                                    this.props.store.clearFetchedScores();
                                }}>
                                Hide currently shown responses
                            </button>
                        </div>
                    </div>
                    <div className="span6 container-fluid">
                        <div className="span6">
                            <ScoreSelect />
                        </div>
                        <div className="span6">
                            <StudyTypeSelect />
                        </div>
                        <p className="help-block">
                            To de-select a filter, click on the filter while holding Control on
                            Windows or ⌘ on Mac
                        </p>
                    </div>
                </div>
                <MetricForm />
                <ScoreList />
            </div>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
