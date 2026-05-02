import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import DisplayComponent from "../components/AggregateGraph";

@inject("store")
@observer
class AggregateGraph extends Component {
    render() {
        const {store} = this.props,
            domains = store.formatRobForAggregateDisplay,
            noFinalReviews = _.isEmpty(domains);
        return noFinalReviews ? (
            <div className="container">
                <span className="alert alert-warning col-12">
                    A final reviewer assignment is required.
                </span>
            </div>
        ) : (
            <DisplayComponent
                domains={domains}
                handleSelectDomain={store.selectDomain}
                handleSelectMetric={store.selectMetric}
            />
        );
    }
}

AggregateGraph.propTypes = {
    store: PropTypes.object,
};

export default AggregateGraph;
