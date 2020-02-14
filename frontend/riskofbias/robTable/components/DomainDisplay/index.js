import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import MetricDisplay from "riskofbias/robTable/components/MetricDisplay";
import MetricForm from "riskofbias/robTable/components/MetricForm";

class DomainDisplay extends Component {
    render() {
        let {
            domain,
            config,
            updateNotesRemaining,
            notifyStateChange,
            createScoreOverride,
            deleteScoreOverride,
            robResponseValues,
        } = this.props;
        return (
            <div>
                <h3>{domain.key}</h3>
                {_.map(domain.values, metric => {
                    let props = {
                        key: metric.key,
                        ref: _.last(metric.values).id,
                        metric,
                        config,
                        robResponseValues,
                    };
                    return config.isForm ? (
                        <MetricForm
                            {...props}
                            updateNotesRemaining={updateNotesRemaining}
                            notifyStateChange={notifyStateChange}
                            createScoreOverride={createScoreOverride}
                            deleteScoreOverride={deleteScoreOverride}
                        />
                    ) : (
                        <MetricDisplay {...props} />
                    );
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
    robResponseValues: PropTypes.array.isRequired,
    updateNotesRemaining: PropTypes.func,
    notifyStateChange: PropTypes.func,
    createScoreOverride: PropTypes.func,
    deleteScoreOverride: PropTypes.func,
};

export default DomainDisplay;
