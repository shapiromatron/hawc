import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer, inject} from "mobx-react";
import _ from "lodash";

import Metric from "./Metric";

@inject("store")
@observer
class Domain extends Component {
    render() {
        const {store, domainId} = this.props,
            scores = store.getScoresForDomain(domainId),
            metricIds = _.chain(scores)
                .map(score => score.metric.id)
                .uniq()
                .value(),
            name = scores[0].metric.domain.name;

        return (
            <div>
                <h3>{name}</h3>
                {metricIds.map(metricId => {
                    return <Metric key={metricId} metricId={metricId} />;
                })}
            </div>
        );
    }
}

Domain.propTypes = {
    domainId: PropTypes.number.isRequired,
    store: PropTypes.object,
};

export default Domain;
