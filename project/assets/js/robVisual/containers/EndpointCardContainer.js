import React, { Component } from 'react';
import _ from 'underscore';
import { connect } from 'react-redux';

import EndpointCard from 'robVisual/components/EndpointCard';
import { formatError } from 'robVisual/actions/Filter';
import './EndpointCardContainer.css';


class EndpointCardContainer extends Component {

    componentDidUpdate(){
        let { endpointsLoaded, endpoints, dispatch } = this.props;
        if (endpointsLoaded && endpoints.length === 0) {
            dispatch(formatError('empty'));
        }
    }

    render(){
        let { endpoints } = this.props;
        return (
            <div className='endpointCardContainer'>
                {_.map(endpoints, (ep, i) => { return <EndpointCard key={i} endpoint={ep}/>; })}
            </div>
        );
    }
}

function mapStateToProps(state){
    return {
        endpoints: state.filter.endpoints,
        endpointsLoaded: state.filter.endpointsLoaded,
    };
}

export default connect(mapStateToProps)(EndpointCardContainer);
