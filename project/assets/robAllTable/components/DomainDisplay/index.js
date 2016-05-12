import React, { Component, PropTypes } from 'react';

import MetricDisplay from 'robAllTable/components/MetricDisplay';


class DomainDisplay extends Component {

    render(){
        let { domain } = this.props;
        return (
            <div>
                <h3>{domain.key}</h3>
                {_.map(domain.values, (metric) => {
                    return <MetricDisplay key={metric.key} metric={metric}/>;
                })}
            </div>
        );
    }

}

DomainDisplay.propTypes = {
    domain: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.array.isRequired,
    }).isRequired,
};

export default DomainDisplay;
