import React, { Component, PropTypes } from 'react';

import MetricDisplay from 'robTable/components/MetricDisplay';


class DomainDisplay extends Component {

    render(){
        let { domain, config } = this.props;
        return (
            <div>
                <h3>{domain.key}</h3>
                {_.map(domain.values, (metric) => {
                    return <MetricDisplay key={metric.key}
                                          ref={_.last(metric.values).id}
                                          metric={metric}
                                          config={config} />;
                })}
                <hr/>
            </div>
        );
    }

}

DomainDisplay.propTypes = {
    domain: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.array.isRequired,
    }).isRequired,
    config: PropTypes.object,
};

export default DomainDisplay;
