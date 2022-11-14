import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Spacer from "shared/components/Spacer";

import Metric from "./Metric";

@inject("store")
@observer
class Domain extends Component {
    render() {
        const {store, domainId} = this.props,
            metricIds = store.getMetricIds(domainId),
            name = store.domains[domainId].name;

        return (
            <>
                <h3>{name}</h3>
                {metricIds.map(metricId => {
                    return <Metric key={metricId} metricId={metricId} />;
                })}
                <Spacer />
            </>
        );
    }
}

Domain.propTypes = {
    domainId: PropTypes.number.isRequired,
    store: PropTypes.object,
};

export default Domain;
