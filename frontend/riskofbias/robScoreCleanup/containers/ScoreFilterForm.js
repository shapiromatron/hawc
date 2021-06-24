import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Loading from "shared/components/Loading";

import MetricSelect from "../components/MetricSelect";
import ScoreSelect from "../components/ScoreSelect";
import StudyTypeSelect from "../components/StudyTypeSelect";

@inject("store")
@observer
class ScoreFilterForm extends Component {
    render() {
        const {store} = this.props,
            {isLoading} = store;

        if (isLoading) {
            return <Loading />;
        }

        return (
            <div className="row cleanStudyMetricForm">
                <div className="col-md-6">
                    <MetricSelect store={store} />
                    <div>
                        <button className="btn btn-primary" onClick={() => store.fetchScores()}>
                            Load responses
                        </button>
                        <button
                            className="btn btn-secondary ml-2"
                            onClick={() => store.clearFetchedScores()}>
                            Hide currently shown responses
                        </button>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="row">
                        <div className="col-md-6">
                            <ScoreSelect store={store} />
                        </div>
                        <div className="col-md-6">
                            <StudyTypeSelect store={store} />
                        </div>
                    </div>
                    <p className="form-text text-muted">
                        To de-select a filter, click on the filter while holding Control on Windows
                        or ⌘ on Mac
                    </p>
                </div>
            </div>
        );
    }
}
ScoreFilterForm.propTypes = {
    store: PropTypes.object,
};

export default ScoreFilterForm;
