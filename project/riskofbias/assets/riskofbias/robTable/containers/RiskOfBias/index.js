import React, { Component } from 'react';
import { connect } from 'react-redux';

import AggregateGraph from 'riskofbias/robTable/containers/AggregateGraph';
import RiskOfBiasForm from 'riskofbias/robTable/containers/RiskOfBiasForm';
import RiskOfBiasDisplay from 'riskofbias/robTable/containers/RiskOfBiasDisplay';

class RiskOfBias extends Component {
    render() {
        return this.props.isForm ? (
            <RiskOfBiasForm />
        ) : (
            <div>
                <AggregateGraph />
                <hr />
                <RiskOfBiasDisplay />
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        isForm: state.config.isForm,
    };
}

export default connect(mapStateToProps)(RiskOfBias);
