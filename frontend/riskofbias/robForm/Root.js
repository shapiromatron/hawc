import React, {Component} from "react";
import PropTypes from "prop-types";

// import {connect} from "react-redux";
// import _ from "lodash";

// import {
//     fetchFullStudyIfNeeded,
//     submitRiskOfBiasScores,
//     scoreStateChange,
//     createScoreOverride,
//     deleteScoreOverride,
// } from "riskofbias/robTable/actions";
// import Completeness from "riskofbias/robTable/components/Completeness";
// import DomainDisplay from "riskofbias/robTable/components/DomainDisplay";
// import Loading from "shared/components/Loading";
// import ScrollToErrorBox from "shared/components/ScrollToErrorBox";

class Root extends Component {
    constructor(props) {
        super(props);
        this.state = {
            notesLeft: new Set(),
        };
    }

    componentWillMount() {
        this.props.store.fetchFullStudyIfNeeded();
    }

    submitForm(e) {
        e.preventDefault();
        this.props.store.submitRiskOfBiasScores();
    }

    handleNotifyStateChange(payload) {
        this.props.store.scoreStateChange(payload);
    }

    handleCreateScoreOverride(payload) {
        this.props.store.createScoreOverride(payload);
    }

    handleDeleteScoreOverride(payload) {
        this.props.store.deleteScoreOverride(payload);
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

Root.propTypes = {
    store: PropTypes.shape({
        createScoreOverride: PropTypes.func.isRequired,
        deleteScoreOverride: PropTypes.func.isRequired,
        fetchFullStudyIfNeeded: PropTypes.func.isRequired,
        scoreStateChange: PropTypes.func.isRequired,
        submitRiskOfBiasScores: PropTypes.func.isRequired,
    }).isRequired,
};

export default Root;
