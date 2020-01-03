import React, { Component } from 'react';
import { connect } from 'react-redux';

import { resetError } from 'riskofbias/robScoreCleanup/actions/Errors';
import { fetchMetricOptions } from 'riskofbias/robScoreCleanup/actions/Metrics';
import { fetchScoreOptions } from 'riskofbias/robScoreCleanup/actions/Scores';
import { fetchStudyTypeOptions } from 'riskofbias/robScoreCleanup/actions/StudyTypes';
import {
    fetchItemScores,
    clearItemScores,
    updateEditMetricIfNeeded,
} from 'riskofbias/robScoreCleanup/actions/Items';

import ScrollToErrorBox from 'shared/components/ScrollToErrorBox';
import MetricForm from 'riskofbias/robScoreCleanup/containers/MetricForm';
import MetricSelect from 'riskofbias/robScoreCleanup/containers/MetricSelect';
import ScoreList from 'riskofbias/robScoreCleanup/containers/ScoreList';
import ScoreSelect from 'riskofbias/robScoreCleanup/containers/ScoreSelect';
import StudyTypeSelect from 'riskofbias/robScoreCleanup/containers/StudyTypeSelect';

import './EditForm.css';

class EditForm extends Component {
    constructor(props) {
        super(props);
        this.loadMetrics = this.loadMetrics.bind(this);
        this.clearMetrics = this.clearMetrics.bind(this);
        this.state = {
            config: {
                display: 'all',
                isForm: 'false',
                riskofbias: {
                    id: 0,
                },
                assessment_id: this.props.config.assessment_id,
            },
        };
    }

    componentWillMount() {
        this.props.dispatch(fetchMetricOptions());
        this.props.dispatch(fetchScoreOptions());
        this.props.dispatch(fetchStudyTypeOptions());
    }

    clearMetrics(e) {
        e.preventDefault();
        this.props.dispatch(resetError());
        this.props.dispatch(clearItemScores());
    }

    loadMetrics(e) {
        e.preventDefault();
        this.props.dispatch(resetError());
        this.props.dispatch(fetchItemScores());
        this.props.dispatch(updateEditMetricIfNeeded());
    }

    submitForm(e) {
        e.preventDefault();
    }

    render() {
        let { error } = this.props,
            { config } = this.state;
        return (
            <div>
                <ScrollToErrorBox error={error} />
                <div className="container-fluid cleanStudyMetricForm">
                    <div className="span6">
                        <MetricSelect />
                        <div>
                            <button className="btn btn-primary space" onClick={this.loadMetrics}>
                                Load responses
                            </button>
                            <button className="btn space" onClick={this.clearMetrics}>
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
                            To de-select a filter, click on the filter while holding ⌘ on Mac or
                            Control on Windows
                        </p>
                    </div>
                </div>
                <MetricForm config={config} />
                <ScoreList config={config} />
            </div>
        );
    }
}
function mapStateToProps(state) {
    const { config, error } = state;
    return {
        config,
        error,
    };
}

export default connect(mapStateToProps)(EditForm);
