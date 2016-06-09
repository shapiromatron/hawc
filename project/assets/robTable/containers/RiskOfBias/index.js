import React, { Component } from 'react';
import { connect } from 'react-redux';

import AggregateGraph from 'robTable/containers/AggregateGraph';
import RiskOfBiasForm from 'robTable/containers/RiskOfBiasForm';
import RiskOfBiasDisplay from 'robTable/containers/RiskOfBiasDisplay';


class RiskOfBias extends Component {

    render() {
        return (
            this.props.isForm ?
                <RiskOfBiasForm /> :
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
