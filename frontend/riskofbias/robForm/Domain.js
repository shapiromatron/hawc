import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";
import _ from "lodash";

import Metric from "./Metric";

@observer
class Domain extends Component {
    render() {
        let scoresByMetric = _.groupBy(this.props.scores, "metric.id"),
            domainName = this.props.scores[0].metric.domain.name;
        return (
            <div>
                <h3>{domainName}</h3>
                {_.map(scoresByMetric, (scores, metricId) => {
                    const intMetricId = parseInt(metricId);
                    return <Metric key={intMetricId} metricId={intMetricId} scores={scores} />;
                })}
            </div>
        );
    }
}

Domain.propTypes = {
    domainId: PropTypes.number.isRequired,
    scores: PropTypes.array.isRequired,
};

export default Domain;
