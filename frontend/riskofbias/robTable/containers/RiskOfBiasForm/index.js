import React, { Component } from 'react';
import { connect } from 'react-redux';
import _ from 'lodash';

import { fetchFullStudyIfNeeded, submitRiskOfBiasScores } from 'riskofbias/robTable/actions';
import Completeness from 'riskofbias/robTable/components/Completeness';
import DomainDisplay from 'riskofbias/robTable/components/DomainDisplay';
import Loading from 'shared/components/Loading';
import ScrollToErrorBox from 'shared/components/ScrollToErrorBox';

class RiskOfBiasForm extends Component {
    constructor(props) {
        super(props);
        this.handleCancel = this.handleCancel.bind(this);
        this.submitForm = this.submitForm.bind(this);
        this.updateNotesLeft = this.updateNotesLeft.bind(this);
        this.state = {
            notesLeft: new Set(),
        };
    }

    componentWillMount() {
        this.props.dispatch(fetchFullStudyIfNeeded());
    }

    submitForm(e) {
        e.preventDefault();
        let scores = _.flattenDeep(
            _.map(this.refs, (domain) => {
                return _.map(domain.refs, (metric) => {
                    let { form } = metric.refs;
                    return {
                        id: form.props.score.id,
                        notes: form.state.notes,
                        score: form.state.score,
                    };
                });
            })
        );
        this.props.dispatch(submitRiskOfBiasScores({ scores }));
    }

    handleCancel(e) {
        e.preventDefault();
        window.location.href = this.props.config.cancelUrl;
    }

    updateNotesLeft(id, action) {
        let notes = this.state.notesLeft;
        if (action === 'clear') {
            notes.delete(id);
            this.setState({ notesLeft: notes });
        } else if (action === 'add') {
            notes.add(id);
            this.setState({ notesLeft: notes });
        }
    }

    render() {
        let { itemsLoaded, riskofbiases, error, config, robResponseValues } = this.props;
        if (!itemsLoaded) return <Loading />;
        return (
            <div className="riskofbias-display">
                <ScrollToErrorBox error={error} />
                <form onSubmit={this.submitForm}>
                    {_.map(riskofbiases, (domain) => {
                        return (
                            <DomainDisplay
                                key={domain.key}
                                ref={domain.key}
                                domain={domain}
                                config={config}
                                updateNotesLeft={this.updateNotesLeft}
                                robResponseValues={robResponseValues}
                            />
                        );
                    })}
                    <Completeness number={this.state.notesLeft} />
                    <button className="btn btn-primary space" type="submit">
                        Save changes
                    </button>
                    <button className="btn space" onClick={this.handleCancel}>
                        Cancel
                    </button>
                </form>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
        itemsLoaded: state.study.itemsLoaded,
        riskofbiases: state.study.riskofbiases,
        robResponseValues: state.study.rob_response_values,
        error: state.study.error,
    };
}

export default connect(mapStateToProps)(RiskOfBiasForm);
