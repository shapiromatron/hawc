import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";
import MetricForm from "./MetricForm";
import MetricSelect from "./MetricSelect";
import ScoreList from "./ScoreList";
import ScoreSelect from "./ScoreSelect";
import StudyTypeSelect from "./StudyTypeSelect";

import "./Main.css";

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
                <div className="row cleanStudyMetricForm">
                    <div className="col-md-6">
                        <MetricSelect />
                        <div>
                            <button
                                className="btn btn-primary"
                                onClick={() => {
                                    this.props.store.fetchScores();
                                }}>
                                Load responses
                            </button>
                            <button
                                className="btn btn-secondary ml-2"
                                onClick={() => {
                                    this.props.store.clearFetchedScores();
                                }}>
                                Hide currently shown responses
                            </button>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="row">
                            <div className="col-md-6">
                                <ScoreSelect />
                            </div>
                            <div className="col-md-6">
                                <StudyTypeSelect />
                            </div>
                        </div>
                        <p className="form-text text-muted">
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
