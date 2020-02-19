import React, {Component} from "react";
import {connect} from "react-redux";
import _ from "lodash";

import {
    fetchFullStudyIfNeeded,
    submitRiskOfBiasScores,
    scoreStateChange,
    createScoreOverride,
    deleteScoreOverride,
} from "riskofbias/robTable/actions";
import Completeness from "riskofbias/robForm/Completeness";
import DomainDisplay from "riskofbias/robTable/components/DomainDisplay";
import Loading from "shared/components/Loading";
import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

class RiskOfBiasForm extends Component {
    constructor(props) {
        super(props);
        this.handleCancel = this.handleCancel.bind(this);
        this.submitForm = this.submitForm.bind(this);
        this.handleUpdateNotes = this.handleUpdateNotes.bind(this);
        this.handleNotifyStateChange = this.handleNotifyStateChange.bind(this);
        this.handleCreateScoreOverride = this.handleCreateScoreOverride.bind(this);
        this.handleDeleteScoreOverride = this.handleDeleteScoreOverride.bind(this);
        this.state = {
            notesLeft: new Set(),
        };
    }

    componentWillMount() {
        this.props.dispatch(fetchFullStudyIfNeeded());
    }

    submitForm(e) {
        e.preventDefault();
        this.props.dispatch(submitRiskOfBiasScores());
    }

    handleCancel(e) {
        e.preventDefault();
        window.location.href = this.props.config.cancelUrl;
    }

    handleUpdateNotes(id, action) {
        let notes = this.state.notesLeft;
        if (action === "clear") {
            notes.delete(id);
            this.setState({notesLeft: notes});
        } else if (action === "add") {
            notes.add(id);
            this.setState({notesLeft: notes});
        }
    }

    handleNotifyStateChange(payload) {
        this.props.dispatch(scoreStateChange(payload));
    }

    handleCreateScoreOverride(payload) {
        this.props.dispatch(createScoreOverride(payload));
    }

    handleDeleteScoreOverride(payload) {
        this.props.dispatch(deleteScoreOverride(payload));
    }

    render() {
        let {itemsLoaded, riskofbiases, error, config, robResponseValues} = this.props;
        if (!itemsLoaded) return <Loading />;
        return (
            <div className="riskofbias-display">
                <ScrollToErrorBox error={error} />
                <form onSubmit={this.submitForm}>
                    {_.map(riskofbiases, domain => {
                        return (
                            <DomainDisplay
                                key={domain.key}
                                ref={domain.key}
                                domain={domain}
                                config={config}
                                updateNotesRemaining={this.handleUpdateNotes}
                                notifyStateChange={this.handleNotifyStateChange}
                                createScoreOverride={this.handleCreateScoreOverride}
                                deleteScoreOverride={this.handleDeleteScoreOverride}
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
