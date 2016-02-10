import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';
import EndpointCard from 'robVisual/components/EndpointCard';

class EndpointCardContainer extends Component {

    render(){
        let eps = [1,2,3,1,2,3,1,2,3];
        return (
            <div className='row-fluid'>
                {_.map(eps, (ep, i) => { return <EndpointCard key={i} />; })}
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        endpoints: state.filter.endpoints,
    };
}

export default connect(mapStateToProps)(EndpointCardContainer);
