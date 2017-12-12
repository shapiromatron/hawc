import React, { Component } from 'react';
import _ from 'lodash';
import { connect } from 'react-redux';

import EndpointCard from 'riskofbias/robVisual/components/EndpointCard';
import { formatError } from 'riskofbias/robVisual/actions/Filter';
import './EndpointCardContainer.css';

class EndpointCardContainer extends Component {
    componentDidUpdate() {
        let { endpointsLoaded, endpoints, dispatch } = this.props;
        if (endpointsLoaded && endpoints.length === 0) {
            dispatch(formatError('empty'));
        }
    }

    render() {
        let { endpoints, studies } = this.props;
        return (
            <div className="endpointCardContainer">
                {_.map(endpoints, (ep, i) => {
                    return (
                        <EndpointCard
                            key={i}
                            study={_.find(studies, {
                                id: ep.animal_group.experiment.study.id,
                            })}
                            endpoint={ep}
                        />
                    );
                })}
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        endpoints: state.filter.endpoints,
        endpointsLoaded: state.filter.endpointsLoaded,
        studies: state.filter.robScores,
    };
}

export default connect(mapStateToProps)(EndpointCardContainer);
