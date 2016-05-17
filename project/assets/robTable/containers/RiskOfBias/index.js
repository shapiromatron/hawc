import React, { Component } from 'react';
import { connect } from 'react-redux';

import AggregateGraph from 'robTable/containers/AggregateGraph';
import ConflictResolutionForm from 'robTable/containers/ConflictResolutionForm';
import RiskOfBiasDisplay from 'robTable/containers/RiskOfBiasDisplay';


class RiskOfBias extends Component {

    render() {
        return (
            this.props.isForm ?
                <ConflictResolutionForm /> :
                <div>
                    <AggregateGraph />
                    <RiskOfBiasDisplay />
                </div>
        );
    }
}

function mapStateToProps(state){
    return {
        isForm: state.config.isForm,
    };
}

export default connect(mapStateToProps)(RiskOfBias);
