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
                            handleClick={props.handleClick}
                        />
                    );
                })}
            </div>
            <div className="footer muted">Click on any cell above to view details.</div>
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
    handleClick: PropTypes.func,
};

export default AggregateGraph;
