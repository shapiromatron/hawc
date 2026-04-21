import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";

import MetricDisplay from "./MetricDisplay";

class DomainDisplay extends Component {
    render() {
        let {domain, config} = this.props;
        return (
            <div>
                <h3>{domain.key}</h3>
                {_.map(domain.values, metric => {
                    let props = {
                        key: metric.key,
                        ref: _.last(metric.values).id,
                        metric,
                        config,
                    };
                    return <MetricDisplay {...props} />;
                })}
                <hr />
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
