import _ from "lodash";
import React from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";

import DomainCell from "./DomainCell";

import "./AggregateGraph.css";

const AggregateGraph = props => {
    return (
        <div className="aggregate-graph">
            <div className="aggregate-flex">
                {_.map(props.domains, domain => {
                    return (
                        <DomainCell
                            key={domain.key}
                            domain={domain}
                            handleSelectDomain={props.handleSelectDomain}
                            handleSelectMetric={props.handleSelectMetric}
                        />
                    );
                })}
            </div>
            <div className="text-muted">Click on any cell above to view details.</div>
        </div>
    );
};

export function renderAggregateGraph(data, element) {
    ReactDOM.render(
        <AggregateGraph domains={data.domains} handleClick={data.handleClick} />,
        element
    );
}

AggregateGraph.propTypes = {
    domains: PropTypes.array,
    handleSelectDomain: PropTypes.func.isRequired,
    handleSelectMetric: PropTypes.func.isRequired,
};

export default AggregateGraph;
